from texttable import *
from blessed import Terminal

class Blessedtable(Texttable):
    
    def __init__(self, 
                 max_width=80, 
                 border_format=None, 
                 header_format=None,
                 column_format=None):
        self.term = Terminal()
        self._border_format = border_format
        self._header_format = header_format
        self._column_format = column_format
        self._border_formatter = None
        self._header_formatter = []
        self._column_formatter = []
        self._column = None

        self.set_max_width(max_width)
        self._precision = 3
        self._deco = Texttable.VLINES | Texttable.HLINES | Texttable.BORDER | \
            Texttable.HEADER
        # self.set_chars(['-', '|', '+', '='])
        self.reset()
    
    @property
    def border_format(self):
        return self._border_format
    
    @border_format.setter
    def border_format(self, value):
        self._border_format = value  
        self._init_formatters()  

    @property
    def header_format(self):
        return self._header_format
    
    @header_format.setter
    def header_format(self, value):
        self._header_format = value
        self._init_formatters()
    
    @property
    def column_format(self):
        return self._column_format
    
    @column_format.setter
    def column_format(self, value):
        self._column_format = value
        self._init_formatters()
    
    def _init_formatters(self):
        """Initialize cell formatters.
        - num_columns defines the number of columns in the table
        """
        assert self._num_columns is not None, "Add rows first in roder to determine the number of columns"
        
        self._hline_string = None
        self._header_formatter = []
        self._column_formatter = []
        # self._header = []


        self._border_formatter = self.term.formatter('normal_on_normal') if self._border_format is None else self.term.formatter(self._border_format)
        self.set_chars(['-', '|', '+', '='])
        num_columns = self._num_columns
        
        if self._column_format is None:
            for i in range(num_columns):
                self._column_formatter.append(self.term.formatter("normal_on_normal"))
        elif isinstance(self._column_format, str):
            for i in range(num_columns):
                self._column_formatter.append(self.term.formatter(self._column_format))
        elif isinstance(self._column_format, list):
            assert len(self._column_format) == num_columns, "%s columns formats required, found %s" % (num_columns, len(self._column_format)) 
            for cf in self._column_format:
                self._column_formatter.append(self.term.formatter(cf))       
        else:
            raise ValueError("column_format is not a valid argument")

        if self._header_format is None:
            self._header_formatter = self._column_formatter
        elif isinstance(self._header_format, str):
            for i in range(num_columns):
                self._header_formatter.append(self.term.formatter(self._header_format))
        elif isinstance(self._header_format, list):
            assert len(self._header_format) == num_columns, "%s header formats required" % num_columns 
            for hf in self._header_format:
                self._header_formatter.append(self.term.formatter(hf))       
        else:
            raise ValueError("header_format is not a valid argument")
        
        if self._column_format is None and self._header_format is not None:
            self._column_formatter = self._header_formatter
          
    def add_rows(self, rows, header=True):
        """Add several rows in the rows stack

        - The 'rows' argument can be either an iterator returning arrays,
          or a by-dimensional array
        - 'header' specifies if the first row should be used as the header
          of the table
        """
        self._num_columns = len(rows[0])
        self._init_formatters()
        # nb: don't use 'iter' on by-dimensional arrays, to get a
        #     usable code for python 2.1
        if header:
            if hasattr(rows, '__iter__') and hasattr(rows, 'next'):
                self.header(rows.next())
            else:
                self.header(rows[0])
                rows = rows[1:]
        for row in rows:
            self.add_row(row)
        return self
    
    def set_chars(self, array):
        """Set the characters used to draw lines between rows and columns

        - the array should contain 4 fields:

            [horizontal, vertical, corner, header]

        - default is set to:

            ['-', '|', '+', '=']
        """

        if len(array) != 4:
            raise ArraySizeError("array should contain 4 characters")
        array = [ x[:1] for x in [ str(s) for s in array ] ]
        (self._char_horiz, self._char_vert,
            self._char_corner, self._char_header) = [self._border_formatter(s) for s in array]
        return self
    
    def _draw_line(self, line, isheader=False):
        """Draw a line

        Loop over a single cell length, over all the cells
        """
        line = self._splitit(line, isheader)
        space = " "
        out = ""
        formatter = self._header_formatter if isheader else self._column_formatter
        for i in range(len(line[0])):
            if self._has_border():
                out += "%s%s" % (self._char_vert, formatter[0](space))
            length = 0
            column_num = 0
            for cell, width, align in zip(line, self._width, self._align):
                # out += "%s" % self._column_formatter[0](space) if column_num == 0 else ""
                space_ = space
                length += 1
                cell_line = cell[i]
                fill = width - len(cell_line)
                if isheader:
                    align = self._header_align[length - 1]
                if align == "r":
                    out += formatter[column_num](fill * space + cell_line)
                elif align == "c":
                    out += formatter[column_num]((int(fill/2) * space + cell_line \
                                + int(fill/2 + fill%2) * space))
                else:
                    out += formatter[column_num](cell_line + fill * space)
                if length < len(line):
                    out += "%s%s%s" % (formatter[column_num](space), [formatter[column_num](space), self._char_vert][self._has_vlines()], formatter[column_num+1](space))
                column_num += 1
                
            out += "%s\n" % ['', formatter[len(formatter)-1](" ") + self._char_vert][self._has_border()]
        return out
   
    def _build_hline(self, is_header=False):
        """Return a string used to separated rows or separate header from
        rows
        """
        horiz = self._char_horiz
        if (is_header):
            horiz = self._char_header
        # compute cell separator
        s = "%s%s%s" % (horiz, [horiz, self._char_corner][self._has_vlines()],
            horiz)
        # build the line
        l = s.join([horiz * n for n in self._width])
        # add border if needed
        if self._has_border():
            l = "%s%s%s%s%s\n" % (self._char_corner, horiz, l, horiz,
                self._char_corner)
            # l = self._border_formatter(l)
        else:
            l += "\n"
        return l
    
    def draw(self):
        """Draw the table

        - the table is returned as a whole string
        """

        if not self._header and not self._rows:
            return
        self._compute_cols_width()
        self._check_align()
        out = ""
        if self._has_border():
            out += self._hline()
        if self._header:
            out += self._draw_line(self._header, isheader=True)
            if self._has_header():
                out += self._hline_header()
        length = 0
        for row in self._rows:
            length += 1
            out += self._draw_line(row)
            if self._has_hlines() and length < len(self._rows):
                out += self._hline()
        if self._has_border():
            out += self._hline()
        return out[:-1]


# import texttable

# print("t?

# table = Texttable()
# table.set_cols_align(["l", "r", "c"])
# table.set_cols_valign(["t", "m", "b"])
# table.add_rows([["Name", "Age", "Nickname"],
#     ["Mr\nXavier\nHuon", 32, "Xav'"],
#     ["Mr\nBaptiste\nClement", 1, "Baby"],
#     ["Mme\nLouise\nBourgeau", 28, "Lou\n\nLoue"]])

# for i in [4,6,14]:
#     table.set_deco(i)
#     print(table.draw())
#     print()

# table = Blessedtable(header_format='green_on_blue', border_format='blue_on_red')
# table.set_cols_align(["l", "r", "c"])
# table.set_cols_valign(["t", "m", "b"])
# table.add_rows([["Name", "Age", "Nickname"],
#     ["Mr\nXavier\nHuon", 32, "Xav'"],
#     ["Mr\nBaptiste\nClement", 1, "Baby"],
#     ["Mme\nLouise\nBourgeau", 28, "Lou\n\nLoue"]])

# for i in range(15,16):
#     # print(i)
#     table.set_deco(i)
#     print(table.draw())
#     print(table.header_format)
# #  = None
#     # table.reset()
#     hf = ['green', 'italic_blue', 'purple']
#     cf = ['white_on_green', 'italic_orange_on_blue', 'teal']
#     table.header_format = hf
#     table.border_format = 'yellow'
#     # table.column_format = cf
#     print(table.draw())
#     print(table.border_format)
    
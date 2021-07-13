from texttable import Texttable, ArraySizeError
from blessed import Terminal

class Blessedtable(Texttable):
    
    def __init__(self, 
                 max_width=80, 
                 border_format=None, 
                 header_format=None,
                 column_format=None):
        self.term = Terminal()
        # self.border_format = border_format
        self.header_format = header_format
        self.column_format = column_format
        self.border_formatter = self.term.formatter('normal_on_normal') if not border_format else self.term.formatter(border_format)
        self.header_formatter = []
        self.column_formatter = []
        # self.cell_formatter = self.term.formatter('normal_on_normal') if not cell_format else self.term.formatter(cell_format)
        # self.header_formatter = None if not header_format else self.term.formatter(header_format)

        # self.column_formatter = []
        # None if not header_format else self.term.formatter(header_format)
        # if column_format is not None:
        #     if isinstance(header_format, str):
        #         d
        #     elif isinstance(header_format, list):
        #         for cf in column_format:
        #             self.column_formatter.append(self.term.formatter(cf))
        # else:
                

        self.set_max_width(max_width)
        self._precision = 3
        self._deco = Texttable.VLINES | Texttable.HLINES | Texttable.BORDER | \
            Texttable.HEADER
        self.set_chars(['-', '|', '+', '='])
        self.reset()
    
    def _init_formatters(self, num_columns):
        """Initialize cell formatters.
        - num_columns defines the number of columns in the table
        """
        
        if self.column_format is None:
            for i in range(num_columns):
                self.column_formatter.append(self.term.formatter("normal_on_normal"))
        elif isinstance(self.column_format, str):
            for i in range(num_columns):
                self.column_formatter.append(self.term.formatter(self.column_format))
        elif isinstance(self.column_format, list):
            assert len(self.column_format) == num_columns, "%s columns formats required, found %s" % (num_columns, len(self.column_format)) 
            for cf in self.column_format:
                self.column_formatter.append(self.term.formatter(cf))       
        else:
            raise ValueError("column_format is not a valid argument")

        if self.header_format is None:
            self.header_formatter = self.column_formatter
        elif isinstance(self.header_format, str):
            for i in range(num_columns):
                self.header_formatter.append(self.term.formatter(self.header_format))
        elif isinstance(self.header_format, list):
            assert len(self.header_format) == num_columns, "%s header formats required" % num_columns 
            for hf in self.header_format:
                self.header_formatter.append(self.term.formatter(hf))       
        else:
            raise ValueError("header_format is not a valid argument")
        
    
    def add_rows(self, rows, header=True):
        """Add several rows in the rows stack

        - The 'rows' argument can be either an iterator returning arrays,
          or a by-dimensional array
        - 'header' specifies if the first row should be used as the header
          of the table
        """

        self._init_formatters(len(rows[0]))
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
            self._char_corner, self._char_header) = [self.border_formatter(s) for s in array]
        return self
    
    def _draw_line(self, line, isheader=False):
        """Draw a line

        Loop over a single cell length, over all the cells
        """
        line = self._splitit(line, isheader)
        space = " "
        out = ""
        for i in range(len(line[0])):
            if self._has_border():
                if isheader:
                    out += "%s%s" % (self._char_vert, self.header_formatter[0](space))
                else:
                    out += "%s%s" % (self._char_vert, self.column_formatter[0](space))
            length = 0
            column_num = 0
            for cell, width, align in zip(line, self._width, self._align):
                # out += "%s" % self.column_formatter[0](space) if column_num == 0 else ""
                space_ = space
                length += 1
                cell_line = cell[i]
                fill = width - len(cell_line)
                if isheader:
                    align = self._header_align[length - 1]
                if align == "r":
                    if isheader:
                        out += self.header_formatter[column_num](fill * space + cell_line)
                    else:
                        out += self.column_formatter[column_num](fill * space + cell_line)
                elif align == "c":
                    if isheader:
                        out += self.header_formatter[column_num]((int(fill/2) * space + cell_line \
                                + int(fill/2 + fill%2) * space))
                    else:
                        out += self.column_formatter[column_num]((int(fill/2) * space + cell_line \
                                + int(fill/2 + fill%2) * space))
                else:
                    if isheader:
                        out += self.header_formatter[column_num](cell_line + fill * space)
                    else:
                        out += self.column_formatter[column_num](cell_line + fill * space)
                if length < len(line):
                    if isheader:
                        out += "%s%s%s" % (self.header_formatter[column_num](space), [self.header_formatter[column_num](space), self._char_vert][self._has_vlines()], self.header_formatter[column_num+1](space))
                    else:
                        out += "%s%s%s" % (self.column_formatter[column_num](space), [self.column_formatter[column_num](space), self._char_vert][self._has_vlines()], self.column_formatter[column_num+1](space))
                column_num += 1
            if isheader:
                out += "%s\n" % ['', self.header_formatter[len(self.column_formatter)-1](" ") + self._char_vert][self._has_border()]
            else:
                out += "%s\n" % ['', self.column_formatter[len(self.column_formatter)-1](" ") + self._char_vert][self._has_border()]
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
            # l = self.border_formatter(l)
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
  
# bold underline reverse blink italic standout
cf = ['black_on_white', 'pink_on_magenta', 'green_on_purple']
# cf = 'turquoise_on_orange'
hf = ['black_on_white', 'pink_on_magenta', 'green_on_yellow']

# hf = 'white_on_teal'
# hf=None
table = Blessedtable(border_format='green', 
                     header_format=hf,
                     column_format=cf)
# table = Texttable()
# table.set_cols_align(["c", "l", "r", "r", "c"])
# table.set_cols_valign(["t", "m", "b", "t", "b"])
table.add_rows([["Name", "Age", "Nickname"],
                ["Mr\nXavier\nHuon", 32, "Xav'"],
                ["Mr\nBaptiste\nClement", 1, "Baby"],
                ["Mme\nLouise\nBourgeau", 28, "Lou\n\nLoue"]])




# table.set_deco(7)
# table.set_cols_dtype(['t',  # text
#                     'f',  # float (decimal)
#                     'e',  # float (exponent)
#                     'i',  # integer
#                     'a']) # automatic
# table.set_cols_align(["c", "r", "r", "r", "l"])
# table.add_rows([["text",    "float", "exp", "int", "auto"],
#                 ["abcdfd\nfdfhdfhfghjd",    "67",    654,   89,    128.001],
#                 ["efghijk", 67.5434, .654,  89.6,  12800000000000000000000.00023],
#                 ["lmn",     5e-78,   5e-78, 89.4,  .000000000000128],
#                 ["opqrstu", .023,    5e+78, 92.,   12800000000000000000000]])
print(table.draw())
# print(table._deco)

# print(len(table._rows[0]))
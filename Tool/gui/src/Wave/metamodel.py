import wx
import Wave
from Wave import grid

class UnaryPrefixOperatorToCurrentPage:

    def __init__(self, operator, prefix):
        self.operator = operator
        self.prefix = prefix

    def __call__(self, frame):
        current_page_index = frame.notebook.GetSelection()
        result_name = self.prefix + frame.notebook.GetPageText(current_page_index)
        current_grid_table = frame.current_grid_table()        
        result_grid_table = Wave.grid.apply_to_grid_tables(self.operator, current_grid_table)
        frame.notebook.new_page(result_grid_table, result_name)

class BinaryInfixOperatorToSelectedPages: 

    def __init__(self, operator, infix):
        self.operator = operator
        self.infix = infix

    def __call__(self, frame):
        page_index_1 = frame.select_page_index()
        page_index_2 = frame.select_page_index()
        result_name = frame.notebook.GetPageText(page_index_1) + self.infix + frame.notebook.GetPageText(page_index_2)
        grid_table_1 = frame.get_grid_table(page_index_1)
        grid_table_2 = frame.get_grid_table(page_index_2)
        result_grid_table = Wave.grid.apply_to_grid_tables(self.operator, grid_table_1, grid_table_2)
        frame.notebook.new_page(result_grid_table, result_name)

class BinaryFunctionToSelectedPages:

    def __init__(self, function, name):
        self.function = function
        self.name = name

    def __call__(self, frame):
        page_index_1 = frame.select_page_index()
        page_index_2 = frame.select_page_index()
        name_1 = frame.notebook.GetPageText(page_index_1)
        name_2 = frame.notebook.GetPageText(page_index_2)
        grid_table_1 = frame.get_grid_table(page_index_1)
        grid_table_2 = frame.get_grid_table(page_index_2)
        result_name = self.name + '(' + name_1 + ', ' + name_2 + ')'
        result_grid_table = Wave.grid.apply_to_grid_tables(self.function, grid_table_1, grid_table_2)
        frame.notebook.new_page(result_grid_table, result_name)

class TernaryFunctionToSelectedPages:

    def __init__(self, function, name):
        self.function = function 
        self.name = name

    def __call__(self, frame):
        page_index_1 = frame.select_page_index()
        page_index_2 = frame.select_page_index()
        page_index_3 = frame.select_page_index()
        name_1 = frame.notebook.GetPageText(page_index_1)
        name_2 = frame.notebook.GetPageText(page_index_2)
        name_3 = frame.notebook.GetPageText(page_index_3)
        grid_table_1 = frame.get_grid_table(page_index_1)
        grid_table_2 = frame.get_grid_table(page_index_2)
        grid_table_3 = frame.get_grid_table(page_index_3)
        result_name = self.name + '(' + name_1 + ', ' + name_2 + ', ' + name_3 + ')'
        result_grid_table = Wave.grid.apply_to_grid_tables(self.function, grid_table_1, grid_table_2, grid_table_3)
        frame.notebook.new_page(result_grid_table, result_name)

class Function():

    def __init__(self, function, fix = False, symbol = False, name = False):
        self.function = function
        self.fix = fix
        self.symbol = symbol
        self.name = name

    def __call__(self, *vargs):
        return self.function(*vargs)

    def get_function(self):
        return self.function

    def nargs(self):
        return self.function.func_code.co_argcount
         
class FunctionWithCallStrategy():

    def __init__(self, function):
        self.function = function
        self.handler = self.apply_strategy()
        
    def get_handler(self):
        return self.handler

    def apply_strategy(self):
        nargs = self.function.nargs()
        if nargs == 1:
            return self.unary_strategy()
        elif nargs == 2:
            return self.binary_strategy()
        elif nargs == 3:
            return self.ternary_strategy()
        else:
            pass

    def unary_strategy(self):
        if ((self.function.fix == 'pre') and self.function.symbol):
            return UnaryPrefixOperatorToCurrentPage(self.function, self.function.symbol)
        else:
            raise Wave.exceptions.WaveMissingCallStrategy

    def binary_strategy(self):
        if ((self.function.fix == 'in') and self.function.symbol):
            return BinaryInfixOperatorToSelectedPages(self.function, self.function.symbol)
        elif ((self.function.fix == False) and self.function.name):
            return BinaryFunctionToSelectedPages(self.function, self.function.name)
        else:
            raise Wave.exceptions.WaveMissingCallStrategy            

    def ternary_strategy(self):
        if ((self.function.fix == False) and self.function.name):
            return TernaryFunctionToSelectedPages(self.function, self.function.name)
        else:
            raise Wave.exceptions.WaveMissingCallStrategy 

class Metamodel():

    def __init__(self):
        self.functions_names_map = {}

    def add_function(self, function, name, long_name):
        self.functions_names_map[function] = {'name': name, 'long_name': long_name}

    def get_name(self, function):
        return self.functions_names_map[function]['name']

    def get_long_name(self, function):
        return self.functions_names_map[function]['long_name']

    def functions(self):
        return self.functions_names_map.keys()

##
# \todo This Menu class ought not to belong to the metamodel module.

class Menu():

    def __init__(self, frame, metamodel, name):
        self.frame = frame
        self.metamodel = metamodel
        self.name = name
        self.init_menus()
        self.bind_handlers()

    def create_handler(self, frame, wave_function):
        def on(event):
            wave_function.handler(frame)
        return on

    def init_menus(self):
        self.frame.mm_sub_menu = wx.Menu()
        self.frame.mm_sub_menu_items = {}
        for wave_function in self.metamodel.functions():
            name = self.metamodel.get_name(wave_function)
            long_name = self.metamodel.get_long_name(wave_function)
            self.frame.mm_sub_menu_items[name] = self.frame.mm_sub_menu.Append(wx.NewId(), name, long_name)
        self.frame.metamodels_menu.AppendSeparator()
        self.frame.metamodels_menu.AppendMenu(-1, self.name, self.frame.mm_sub_menu)  

    def bind_handlers(self):
        for wave_function in self.metamodel.functions():
            name = self.metamodel.get_name(wave_function)
            function = FunctionWithCallStrategy(wave_function)
            handler = self.create_handler(self.frame, function)
            self.frame.Bind(wx.EVT_MENU, handler, self.frame.mm_sub_menu_items[name])


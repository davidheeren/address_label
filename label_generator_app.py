
import customtkinter as ctk
from argparse import Namespace
from pathlib import Path
from typing import Callable
from main import get_args
from label_generator import LabelGenerator

# NOTE: this is my using this library or any python gui lol

OUTER_PADX = 20
OUTER_PADY = 10
INNER_PADX = 5
INNER_PADY = 5
MIN_FRAME_SIZE = 500
BUTTON_WIDTH = 75


class LabelGeneratorApp:
    def __init__(self, inital_args: Namespace, save_options_func: Callable[[Namespace], None]):
        self.root = self._create_root()

        # Backing values for gui options
        self.input_var = ctk.StringVar()
        self.output_var = ctk.StringVar()
        self.filter_var = ctk.StringVar()
        self.bias_var = ctk.StringVar()
        self.ret_var = ctk.BooleanVar()
        self.name_var = ctk.StringVar()
        self.test_var = ctk.BooleanVar()
        self.launch_var = ctk.BooleanVar()
        self.tooltip_var = ctk.StringVar(value="")

        self._set_options(inital_args)
        self.save_options_func = save_options_func
        self.vint_cmd = (self.root.register(self._validate_integer), '%P')
        self.frame_row = 0

        # Setup the UI
        self._setup_input_option()
        self._setup_output_option()
        self._setup_filter_option()
        self._setup_bias_option()
        self._setup_ret_option()
        self._setup_name_option()
        self._setup_test_option()
        self._setup_launch_option()
        self._setup_tasks_bar()
        self._setup_tooltip_bar()

    def _create_root(self) -> ctk.CTk:
        """Creates CTK root and sets vars"""
        ctk.set_appearance_mode("dark")
        ctk.set_widget_scaling(1)
        root = ctk.CTk()
        root.title("Address Label Generator")
        root.geometry("800x900")
        return root

    def _set_options(self, args: Namespace):
        """Sets the option variable from an args"""
        self.input_var.set(args.input)
        self.output_var.set(args.output)
        self.filter_var.set(args.filter)
        self.bias_var.set(args.bias)
        self.ret_var.set(args.ret)
        self.name_var.set(args.name)
        self.test_var.set(args.test)
        self.launch_var.set(args.launch)

    def _get_args_from_options(self) -> Namespace:
        """Returns args from the options"""
        return Namespace(
            input=self.input_var.get(),
            output=self.output_var.get(),
            filter=self.filter_var.get(),
            bias=int(self.bias_var.get()) if self.bias_var.get() else 0,
            ret=self.ret_var.get(),
            name=self.name_var.get(),
            test=self.test_var.get(),
            launch=self.launch_var.get(),
        )

    def _generate_pdf(self):
        """Actually generates the PDF and saves the options config"""
        args = self._get_args_from_options()
        try:
            label_generator = LabelGenerator(args)
            label_generator.generate_pdf()
        except Exception as e:
            self.tooltip_var.set(e)
            print(e)
        self.save_options_func(args)

    def _update_input_var(self):
        """Gets input path from the user"""
        dir_path = Path(self.input_var.get()).parent
        if dir_path == Path("."):
            dir_path = Path.home()
        path = ctk.filedialog.askopenfilename(
            title="Select a File",
            # filetypes=[("Data files", "*.csv *.xlsx"), ("All files", "*.*")],
            filetypes=[("Data files", "*.xlsx"), ("All files", "*.*")],
            initialdir=str(dir_path)
        )
        if not path:
            return
        self.input_var.set(path)

    def _update_output_var(self):
        """Gets the output path from the user"""
        dir_path = Path(self.output_var.get()).parent
        if dir_path == Path("."):
            dir_path = Path.home()
        path = ctk.filedialog.asksaveasfilename(
            title="Select a File",
            defaultextension=".pdf",
            initialfile="labels",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialdir=str(dir_path)
        )
        if not path:
            return
        self.output_var.set(path)

    def _validate_integer(self, new_text: str) -> bool:
        return new_text == "" or new_text.isdigit()

    def _create_frame(self, tooltip_str: str | None) -> ctk.CTkFrame:
        """Creates a frame class with a tooltip"""
        frame = ctk.CTkFrame(self.root)
        frame.grid(row=self.frame_row, column=0, padx=OUTER_PADX, pady=OUTER_PADY, sticky="w")
        frame.grid_columnconfigure(0, weight=1, minsize=MIN_FRAME_SIZE)
        if tooltip_str:
            frame.bind("<Leave>", lambda e: self.tooltip_var.set(""))
            frame.bind("<Enter>", lambda e: self.tooltip_var.set(tooltip_str))
        self.frame_row += 1
        return frame

    # Top left
    def _set_grid_top(self, base: ctk.CTkBaseClass):
        base.grid(row=0, column=0, columnspan=1, padx=INNER_PADX, pady=INNER_PADY, sticky="w")

    # Bottom Left
    def _set_grid_bottom(self, base: ctk.CTkBaseClass):
        base.grid(row=1, column=0, padx=INNER_PADX, pady=INNER_PADY, sticky="w")

    # Bottom Right
    def _set_grid_right(self, base: ctk.CTkBaseClass):
        base.grid(row=1, column=1, padx=INNER_PADX, pady=INNER_PADY, sticky="e")

    def _setup_input_option(self):
        input_frame = self._create_frame("<Input> An Excel file that holds the address data")
        input_header = ctk.CTkLabel(input_frame, text="Input")
        self._set_grid_top(input_header)
        input_widget = ctk.CTkLabel(input_frame, textvariable=self.input_var)
        self._set_grid_bottom(input_widget)
        input_button = ctk.CTkButton(input_frame, text="Choose...", command=self._update_input_var, width=BUTTON_WIDTH)
        self._set_grid_right(input_button)

    def _setup_output_option(self):
        output_frame = self._create_frame("<Output> The path of the pdf that will be created")
        output_header = ctk.CTkLabel(output_frame, text="Output")
        self._set_grid_top(output_header)
        output_widget = ctk.CTkLabel(output_frame, textvariable=self.output_var)
        self._set_grid_bottom(output_widget)
        output_button = ctk.CTkButton(output_frame, text="Choose...", command=self._update_output_var, width=BUTTON_WIDTH)
        self._set_grid_right(output_button)

    def _setup_filter_option(self):
        filter_frame = self._create_frame(
            """
<Filter> Chose which rows from the data to include by order, seperated by commas
* -> all rows
3 -> single row index
4-9 -> range of row indices
mary jane -> match rows by name. all words in the filter must be included in the row to match
! -> removes the filter instead of add
Ex: '*, !5-20, !john, 15' -> adds all rows, removes range 5-10, removes all john rows, then adds row 15
"""
        )
        filter_header = ctk.CTkLabel(filter_frame, text="Filter")
        self._set_grid_top(filter_header)
        filter_widget = ctk.CTkEntry(filter_frame, textvariable=self.filter_var)
        self._set_grid_bottom(filter_widget)

    def _setup_bias_option(self):
        bias_frame = self._create_frame("<Bias> Number of labels to skip before printing. This is for partially used label sheets")
        bias_header = ctk.CTkLabel(bias_frame, text="Bias")
        self._set_grid_top(bias_header)
        bias_widget = ctk.CTkEntry(bias_frame, textvariable=self.bias_var, validate="key", validatecommand=self.vint_cmd)
        self._set_grid_bottom(bias_widget)

    def _setup_ret_option(self):
        ret_frame = self._create_frame("<Ret> Prints your return address for each label")
        ret_widget = ctk.CTkCheckBox(ret_frame, text="Ret", variable=self.ret_var)
        self._set_grid_bottom(ret_widget)

    def _setup_name_option(self):
        name_frame = self._create_frame("<Name> Your name. This specifies which return address to use if the 'Ret' option is enabled. This will remove the row as well")
        name_header = ctk.CTkLabel(name_frame, text="Name")
        self._set_grid_top(name_header)
        name_widget = ctk.CTkEntry(name_frame, textvariable=self.name_var)
        self._set_grid_bottom(name_widget)

    def _setup_test_option(self):
        test_frame = self._create_frame("<Test> Adds a box line around the labels")
        test_widget = ctk.CTkCheckBox(test_frame, text="Test", variable=self.test_var)
        self._set_grid_bottom(test_widget)

    def _setup_launch_option(self):
        launch_frame = self._create_frame("<Launch> Opens the output pdf in the browser when its created")
        launch_widget = ctk.CTkCheckBox(launch_frame, text="Launch", variable=self.launch_var)
        self._set_grid_bottom(launch_widget)

    def _setup_tasks_bar(self):
        task_frame = ctk.CTkFrame(self.root)
        task_frame.grid(row=self.frame_row, column=0, padx=OUTER_PADX, pady=OUTER_PADY, sticky="w")
        task_frame.grid_columnconfigure(0, weight=1, minsize=MIN_FRAME_SIZE / 2)
        task_frame.grid_columnconfigure(1, weight=1, minsize=MIN_FRAME_SIZE / 2)
        self.frame_row += 1

        run_button = ctk.CTkButton(task_frame, text="Run", command=self._generate_pdf, width=BUTTON_WIDTH)
        run_button.grid(row=1, column=0, padx=INNER_PADX, pady=INNER_PADY)

        reset_button = ctk.CTkButton(task_frame, text="Reset Options", command=lambda: self._set_options(get_args(True)), width=BUTTON_WIDTH)
        reset_button.grid(row=1, column=1, padx=INNER_PADX, pady=INNER_PADY)

    def _setup_tooltip_bar(self):
        tooltip_frame = self._create_frame(None)
        tooltip_widget = ctk.CTkLabel(tooltip_frame, textvariable=self.tooltip_var, justify="left")
        self._set_grid_bottom(tooltip_widget)

    def mainloop(self):
        """Runs the app and saves options config on end"""
        self.root.mainloop()
        self.save_options_func(self._get_args_from_options())

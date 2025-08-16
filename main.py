import customtkinter as ctk
from tkinter import filedialog, Menu
import threading
import pandas as pd
import os
import time
from PIL import Image

# --- Your actual OCR logic should be in a file named parsepdf.py ---
try:
    import parsepdf
except ImportError:
    print("Warning: 'parsepdf.py' not found. Using dummy data function.")


    def parse_from_pdf(pdf_path, use_google=False):
        print(f"Simulating OCR processing for: {pdf_path}...")
        time.sleep(3)
        return [
            {'bank_name': 'DUMMY DATA - Erste Bank', 'broj_tekuceg_racuna': '340-DUMMY',
             'platite_racun_br': '908-DUMMY', 'serijski_broj': 'SN-DUMMY-1'},
            {'bank_name': 'DUMMY DATA - OTP Bank', 'broj_tekuceg_racuna': '325-DUMMY',
             'platite_racun_br': '908-DUMMY-2', 'serijski_broj': 'SN-DUMMY-2'},
        ]


    class DummyModule:
        pass


    parsepdf = DummyModule()
    parsepdf.parse_from_pdf = parse_from_pdf


# --------------------------------------------------------------------


class CheckProcessorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Check Data Extractor")
        self.geometry("1200x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Class Attributes ---
        self.data_df = pd.DataFrame()  # Holds all data
        self.selected_pdf_path = ""
        self.csv_file_path = 'results.csv'

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=5, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Check Processor",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.select_pdf_button = ctk.CTkButton(self.sidebar_frame, text="Select PDF", command=self.select_pdf_event)
        self.select_pdf_button.grid(row=1, column=0, padx=20, pady=10)
        self.process_pdf_button = ctk.CTkButton(self.sidebar_frame, text="Process PDF",
                                                command=lambda: self.process_pdf_event(use_google=False),
                                                state="disabled")
        self.process_pdf_button.grid(row=2, column=0, padx=20, pady=10)
        self.process_with_google_button = ctk.CTkButton(self.sidebar_frame, text="Process with Google",
                                                        command=lambda: self.process_pdf_event(use_google=True),
                                                        state="disabled")
        self.process_with_google_button.grid(row=3, column=0, padx=20, pady=10)
        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="Status: Ready", anchor="w")
        self.status_label.grid(row=4, column=0, padx=20, pady=(20, 0))
        self.progressbar = ctk.CTkProgressBar(self.sidebar_frame, mode="indeterminate")

        # --- Main Content Area ---
        self.create_data_display()
        self.load_data_from_csv()

    def create_data_display(self):
        """Creates the main scrollable frame for displaying data cards."""
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Extracted Data")
        self.scrollable_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def populate_data_display(self):
        """Clears and populates the scrollable frame with data cards from self.data_df."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for index, row in self.data_df.iterrows():
            self.create_data_card(row, index)

    def create_data_card(self, data_row, index):
        """Creates a single 'card' for one row of data with a more readable layout."""
        card_frame = ctk.CTkFrame(self.scrollable_frame, border_width=2)
        card_frame.grid(sticky="ew", padx=10, pady=(5, 15))
        card_frame.grid_columnconfigure(0, weight=1)

        # --- Card Header ---
        pdf_name = data_row.get("pdf_name", "N/A")
        page_num = data_row.get("page_num", 0)
        header_text = f"Source: {pdf_name}  |  Page: {page_num}"
        header_label = ctk.CTkLabel(card_frame, text=header_text, font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        header_label.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="ew")

        # --- Main content frame with 2 columns ---
        content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        content_frame.grid_columnconfigure((0, 1), weight=1)

        # --- Left Column: OCR Data ---
        ocr_frame = ctk.CTkFrame(content_frame)
        ocr_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        ocr_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(ocr_frame, text="OCR Data", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 10))

        self.create_entry_field(ocr_frame, "Bank Name:", data_row.get("bank_name", ""), index, "bank_name").pack(
            fill="x", expand=True, padx=10, pady=5)
        self.create_entry_field(ocr_frame, "Platite Račun Br:", data_row.get("platite_racun_br", ""), index,
                                "platite_racun_br").pack(fill="x", expand=True, padx=10, pady=5)
        self.create_entry_field(ocr_frame, "Broj Tekućeg Računa:", data_row.get("broj_tekuceg_racuna", ""), index,
                                "broj_tekuceg_racuna").pack(fill="x", expand=True, padx=10, pady=5)
        self.create_entry_field(ocr_frame, "Serijski Broj:", data_row.get("serijski_broj", ""), index,
                                "serijski_broj").pack(fill="x", expand=True, padx=10, pady=5)

        # --- Right Column: Manual Input & Verification ---
        right_column_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_column_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        right_column_frame.grid_columnconfigure(0, weight=1)

        manual_frame = ctk.CTkFrame(right_column_frame)
        manual_frame.grid(row=0, column=0, sticky="nsew")
        manual_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(manual_frame, text="Manual Input", font=ctk.CTkFont(weight="bold")).pack(pady=(5, 10))

        self.create_entry_field(manual_frame, "Datum Dospeća:", data_row.get("datum_dospeca", ""), index,
                                "datum_dospeca").pack(fill="x", expand=True, padx=10, pady=5)
        self.create_entry_field(manual_frame, "Iznos:", data_row.get("iznos", ""), index, "iznos").pack(fill="x",
                                                                                                        expand=True,
                                                                                                        padx=10, pady=5)
        self.create_entry_field(manual_frame, "Radna Jedinica:", data_row.get("radna_jedinica", ""), index,
                                "radna_jedinica").pack(fill="x", expand=True, padx=10, pady=5)

        # --- Image Buttons ---
        image_frame = ctk.CTkFrame(right_column_frame)
        image_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        image_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(image_frame, text="Image Verification", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0,
                                                                                                   columnspan=2,
                                                                                                   pady=(5, 10))

        upper_img_path = f"{pdf_name}.pdf_{page_num}_upper.png"
        lower_img_path = f"{pdf_name}.pdf_{page_num}_lower.png"
        upper_button = ctk.CTkButton(image_frame, text="Show Upper Image",
                                     command=lambda p=upper_img_path: self.show_image(p))
        upper_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        lower_button = ctk.CTkButton(image_frame, text="Show Lower Image",
                                     command=lambda p=lower_img_path: self.show_image(p))
        lower_button.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    def create_entry_field(self, parent, title, value, index, col_name):
        """Creates a self-contained, editable entry field that saves on focus out."""
        # This frame isolates the label and entry from the parent's layout manager
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")

        label = ctk.CTkLabel(field_frame, text=title, font=ctk.CTkFont(size=12))
        label.pack(fill="x", padx=5, pady=(0, 2))

        entry = ctk.CTkEntry(field_frame)
        entry.pack(fill="x", expand=True, padx=5)
        entry.insert(0, str(value))
        entry.bind("<FocusOut>", lambda event, idx=index, name=col_name: self.on_entry_update(event, idx, name))

        return field_frame

    def on_entry_update(self, event, row_index, column_name):
        """Updates the DataFrame and saves to CSV when an entry field loses focus."""
        new_value = event.widget.get()
        self.data_df.loc[row_index, column_name] = new_value
        self.save_current_data_to_csv()
        self.status_label.configure(text=f"Saved '{column_name}' for row {row_index}")

    def show_image(self, image_path):
        if not os.path.exists(image_path):
            self.status_label.configure(text=f"Error: Image not found at {image_path}")
            return
        image_window = ctk.CTkToplevel(self)
        image_window.title(os.path.basename(image_path))
        image_window.geometry("1200x400")
        image_window.transient(self)
        try:
            pil_image = Image.open(image_path)
            ctk_image = ctk.CTkImage(pil_image, size=pil_image.size)
            image_label = ctk.CTkLabel(image_window, image=ctk_image, text="")
            image_label.pack(padx=20, pady=20, expand=True, fill="both")
        except Exception as e:
            ctk.CTkLabel(image_window, text=f"Failed to load image: {e}").pack(padx=20, pady=20)

    def load_data_from_csv(self):
        if not os.path.exists(self.csv_file_path):
            return
        try:
            self.data_df = pd.read_csv(self.csv_file_path).fillna("")
            self.populate_data_display()
        except Exception as e:
            self.status_label.configure(text=f"Error loading CSV: {e}")

    def select_pdf_event(self):
        self.selected_pdf_path = filedialog.askopenfilename(title="Select a PDF file",
                                                            filetypes=(("PDF Files", "*.pdf"),))
        if self.selected_pdf_path:
            self.status_label.configure(text=f"Selected: {os.path.basename(self.selected_pdf_path)}")
            self.process_pdf_button.configure(state="normal")
            self.process_with_google_button.configure(state="normal")
        else:
            self.status_label.configure(text="Status: No file selected")
            self.process_pdf_button.configure(state="disabled")
            self.process_with_google_button.configure(state="disabled")

    def process_pdf_event(self, use_google=False):
        if not self.selected_pdf_path:
            return
        self.select_pdf_button.configure(state="disabled")
        self.process_pdf_button.configure(state="disabled")
        self.process_with_google_button.configure(state="disabled")
        self.status_label.configure(text="Processing with Google..." if use_google else "Processing...")
        self.progressbar.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.progressbar.start()
        thread = threading.Thread(target=self.run_processing_thread, args=(use_google,), daemon=True)
        thread.start()

    def run_processing_thread(self, use_google):
        """
        Runs the OCR and parsing logic by calling the main function from parsepdf.
        This ensures the correct parser is always used.
        """
        try:
            extracted_data = parsepdf.parse_from_pdf(self.selected_pdf_path, use_google=use_google)
            self.after(0, self.update_ui_with_results, extracted_data)
        except Exception as e:
            self.after(0, self.processing_error, e)

    def update_ui_with_results(self, new_data):
        pdf_name = os.path.basename(self.selected_pdf_path).split('.')[0]
        for i, record in enumerate(new_data):
            record['pdf_name'] = pdf_name
            record['page_num'] = i + 1
        new_df = pd.DataFrame(new_data)
        self.data_df = pd.concat([self.data_df, new_df], ignore_index=True)
        self.save_current_data_to_csv()
        self.populate_data_display()
        self.progressbar.stop()
        self.progressbar.grid_forget()
        self.status_label.configure(text="Status: Complete!")
        self.select_pdf_button.configure(state="normal")
        self.process_pdf_button.configure(state="disabled")
        self.process_with_google_button.configure(state="disabled")

    def processing_error(self, error):
        self.progressbar.stop()
        self.progressbar.grid_forget()
        self.status_label.configure(text=f"Error: {error}")
        self.select_pdf_button.configure(state="normal")
        self.process_pdf_button.configure(state="disabled")
        self.process_with_google_button.configure(state="disabled")

    def save_current_data_to_csv(self):
        required_cols = [
            "pdf_name", "page_num", "bank_name", "platite_racun_br",
            "broj_tekuceg_racuna", "serijski_broj", "datum_dospeca",
            "iznos", "radna_jedinica"
        ]
        for col in required_cols:
            if col not in self.data_df.columns:
                self.data_df[col] = ""
        save_df = self.data_df[required_cols].fillna("")
        save_df.to_csv(self.csv_file_path, index=False)
        print(f"Data saved to {self.csv_file_path}")


if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"E:\DevTools\vision-key.json"
    app = CheckProcessorApp()
    app.mainloop()

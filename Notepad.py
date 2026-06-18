import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, font
import subprocess
import os
import re
import webbrowser
import sys
import ctypes

class AdvancedNotepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Notepad")
        self.root.geometry("800x600")

        
        self.current_font_family = "Segoe UI"
        self.current_font_size = 12
        self.default_font = font.Font(family=self.current_font_family, size=self.current_font_size)
        self.text_widget = tk.Text(self.root, wrap="word", font=self.default_font, undo=True)
        self.text_widget.pack(expand=True, fill="both")

        
        self.text_widget.tag_config("url", foreground="blue", underline=True)
        self.text_widget.tag_bind("url", "<Button-1>", self.open_url)
        self.text_widget.bind("<KeyRelease>", self.highlight_urls)

        self.setup_menu()

    def setup_menu(self):
        menu_bar = tk.Menu(self.root)

        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Print", command=self.print_content)
        file_menu.add_command(label="Command Prompt", command=self.cmd_prompt)
        file_menu.add_command(label="Open After Creating", command=self.open_after_create)
        menu_bar.add_cascade(label="File", menu=file_menu)

        
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="API", command=self.find_api_keys)
        tools_menu.add_command(label="Program Test", command=self.program_test)
        tools_menu.add_command(label="HEX", command=self.toggle_hex)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)

        
        format_menu = tk.Menu(menu_bar, tearoff=0)
        format_menu.add_command(label="Import Custom Font", command=self.import_custom_font)
        menu_bar.add_cascade(label="Format", menu=format_menu)

        self.root.config(menu=menu_bar)

    def new_file(self):
        self.text_widget.delete("1.0", tk.END)

    def open_file(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            with open(filepath, "r", encoding="utf-8") as file:
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, file.read())
            self.current_filepath = filepath
            self.highlight_urls()

    def save_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(self.text_widget.get("1.0", tk.END))
            self.current_filepath = filepath
            return filepath
        return None

    def print_content(self):
        # Creates a temp file, then calls the OS default print command
        temp_file = "temp_print_file.txt"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(self.text_widget.get("1.0", tk.END))
        try:
            os.startfile(temp_file, "print")  # Windows only
        except AttributeError:
            subprocess.run(["lp", temp_file])  # macOS/Linux

    def cmd_prompt(self):
        filepath = self.save_file()
        if filepath:
            command = f"notepad.exe {filepath}"  # Instant execution setup for program/file
            subprocess.Popen(f'start cmd.exe /K "echo Ready to run: {command} & "', shell=True)

    def open_after_create(self):
        filepath = self.save_file()
        if filepath:
            os.startfile(filepath)


    def find_api_keys(self):
        text = self.text_widget.get("1.0", tk.END)
        api_pattern = r'(?i)(api_key|apikey|secret|token)[=\'"]([a-z0-9A-Z]{16,64})'
        matches = re.findall(api_pattern, text)
        if matches:
            keys = "\n".join([f"{match[0]}: {match[1]}" for match in matches])
            messagebox.showinfo("API Keys Found", f"Found potential keys:\n{keys}")
        else:
            messagebox.showinfo("API", "No API keys or secrets detected in the document. oh NO NO FBI DONT GET ME I DIDNT MEAN TO EXPOSE APIS- *gets executed*")

    def program_test(self):
        text = self.text_widget.get("1.0", tk.END)
        temp_name = "test_run.py"
        try:
            with open(temp_name, "w", encoding="utf-8") as f:
                f.write(text)
            
            
            test_window = tk.Toplevel(self.root)
            test_window.title("Program Test Running...")
            test_window.geometry("400x300")
            
            
            tc_font = font.Font(family="Lucida Console", size=11)
            tv = tk.Text(test_window, font=tc_font)
            tv.pack(expand=True, fill="both")
            
           
            proc = subprocess.Popen([sys.executable, temp_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate()
            tv.insert(tk.END, stdout if stdout else stderr)

            def cleanup():
                test_window.destroy()
                if os.path.exists(temp_name):
                    os.remove(temp_name)
                    
            test_window.protocol("WM_DELETE_WINDOW", cleanup)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_hex(self):
        current_text = self.text_widget.get("1.0", tk.END).strip()
        if not current_text:
            return
            
        try:
            if all(c in "0123456789abcdefABCDEF \n" for c in current_text.replace(" ", "")):
           
                bytes_object = bytes.fromhex(current_text.replace(" ", "").replace("\n", ""))
                decoded = bytes_object.decode('utf-8')
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, decoded)
            else:
                # 20 mins
                hex_encoded = current_text.encode('utf-8').hex()
                
                formatted_hex = ' '.join(hex_encoded[i:i+2] for i in range(0, len(hex_encoded), 2))
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, formatted_hex)
        except Exception as e:
            messagebox.showerror("HEX Error", "Failed to toggle hex. Ensure valid hex characters are used.")


    def import_custom_font(self):
        font_path = filedialog.askopenfilename(filetypes=[("Font Files", "*.ttf *.otf")])
        if font_path:
            messagebox.showinfo("Fonts", "Custom Font Imported Successfully. (Note: True font embedding requires specialized OS modules).")

    

    def highlight_urls(self, event=None):
        self.text_widget.tag_remove("url", "1.0", tk.END)
        text = self.text_widget.get("1.0", tk.END)
        # Match domains (.com, .cc, .xyz, etc.)
        url_regex = r'(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}(/[a-zA-Z0-9-._~:/?#@!$&\'()*+,;=]*)?'
        for match in re.finditer(url_regex, text):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.text_widget.tag_add("url", start, end)

    def open_url(self, event):
        index = self.text_widget.index(tk.CURRENT)
        ranges = self.text_widget.tag_ranges("url")
        for i in range(0, len(ranges), 2):
            if self.text_widget.compare(ranges[i], "<=", index) and self.text_widget.compare(index, "<", ranges[i+1]):
                url = self.text_widget.get(ranges[i], ranges[i+1])
                if not url.startswith("http"):
                    url = "http://" + url
                webbrowser.open(url)
                break

    # MIC-RO-PHONE

    def check_easter_eggs(self, event=None):
        text = self.text_widget.get("1.0", tk.END).strip()
        
   
        if "000x0000x0x000000000x80" in text:
            self.root.destroy()
            ctypes.windll.user32.MessageBoxW(0, "Unable to cast object of type 'System.String' to type 'System.Int32'.", "InvalidCastException", 16)
            sys.exit(1)
        elif "cr0j0x10youx7798f" in text:
            self.text_widget.config(bg="black", fg="black", insertbackground="black")
            self.root.update()
            self.root.destroy()
            ctypes.windll.user32.MessageBoxW(0, "Input string was not in a correct format. An attempt to convert text format encountered an unsupported style.", "FormatException", 16)
            sys.exit(1)

       
        elif "M24=REFFILE-.nuget-((>>-?>" in text:
            self.root.withdraw() # Hides the app
            ctypes.windll.user32.MessageBoxW(0, "Unhandled Exception Has Occurred in Your Application. \n\nDetails: Could not load file or assembly 'Newtonsoft.Json, Version=13.0.0.0, Culture=neutral' or one of its dependencies. The system cannot find the file specified.", "Unhandled Exception", 16)
            sys.exit(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedNotepad(root)
    
    
    root.bind("<KeyRelease>", app.check_easter_eggs)
    
    root.mainloop()

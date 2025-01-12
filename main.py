#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Pango', '1.0')
from gi.repository import Gtk, Gdk, GObject, Pango
import os
import paramiko
import threading

class SSHKeyGenerator(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="SSH Key Generator and Tunneling")
        self.set_default_size(400, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)

        self.grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        self.grid.set_margin_top(20)
        self.grid.set_margin_left(20)
        self.grid.set_margin_right(20)
        self.grid.set_margin_bottom(20)
        self.add(self.grid)

        # SSH Key Generation UI
        label_directory = Gtk.Label(label="Directory to Save Keys:")
        self.grid.attach(label_directory, 0, 0, 1, 1)

        self.entry_directory = Gtk.Entry()
        self.grid.attach(self.entry_directory, 1, 0, 1, 1)

        browse_button = Gtk.Button(label="Browse")
        browse_button.connect("clicked", self.browse_directory)
        self.grid.attach(browse_button, 2, 0, 1, 1)

        label_custom_private_key_name = Gtk.Label(label="Custom Private Key Name (without extension):")
        self.grid.attach(label_custom_private_key_name, 0, 1, 1, 1)

        self.entry_custom_private_key_name = Gtk.Entry()
        self.grid.attach(self.entry_custom_private_key_name, 1, 1, 2, 1)

        label_passphrase = Gtk.Label(label="Passphrase for Private Key (optional):")
        self.grid.attach(label_passphrase, 0, 2, 1, 1)

        self.entry_passphrase = Gtk.Entry()
        self.entry_passphrase.set_visibility(False)
        self.grid.attach(self.entry_passphrase, 1, 2, 2, 1)

        label_key_length = Gtk.Label(label="Key Length:")
        self.grid.attach(label_key_length, 0, 3, 1, 1)

        self.key_length_combobox = Gtk.ComboBoxText()
        self.key_length_combobox.append_text("2048")
        self.key_length_combobox.append_text("3072")
        self.key_length_combobox.append_text("4096")
        self.key_length_combobox.set_active(0)
        self.grid.attach(self.key_length_combobox, 1, 3, 2, 1)

        label_key_type = Gtk.Label(label="Key Type:")
        self.grid.attach(label_key_type, 0, 4, 1, 1)

        self.key_type_combobox = Gtk.ComboBoxText()
        self.key_type_combobox.append_text("RSA")
        self.key_type_combobox.append_text("DSA")
        self.key_type_combobox.append_text("ECDSA")
        self.key_type_combobox.set_active(0)
        self.grid.attach(self.key_type_combobox, 1, 4, 2, 1)

        generate_button = Gtk.Button(label="Generate SSH Keys")
        generate_button.connect("clicked", self.generate_ssh_keys)
        self.grid.attach(generate_button, 1, 5, 2, 1)

        view_button = Gtk.Button(label="View SSH Keys")
        view_button.connect("clicked", self.view_ssh_keys)
        self.grid.attach(view_button, 1, 6, 2, 1)

        # SSH Tunneling UI
        label_remote_host = Gtk.Label(label="Remote Host:")
        self.grid.attach(label_remote_host, 0, 7, 1, 1)

        self.entry_remote_host = Gtk.Entry()
        self.grid.attach(self.entry_remote_host, 1, 7, 2, 1)

        label_remote_port = Gtk.Label(label="Remote Port:")
        self.grid.attach(label_remote_port, 0, 8, 1, 1)

        self.entry_remote_port = Gtk.Entry()
        self.grid.attach(self.entry_remote_port, 1, 8, 2, 1)

        label_local_port = Gtk.Label(label="Local Port:")
        self.grid.attach(label_local_port, 0, 9, 1, 1)

        self.entry_local_port = Gtk.Entry()
        self.grid.attach(self.entry_local_port, 1, 9, 2, 1)

        tunnel_button = Gtk.Button(label="Start SSH Tunnel")
        tunnel_button.connect("clicked", self.start_ssh_tunnel)
        self.grid.attach(tunnel_button, 1, 10, 2, 1)

        stop_tunnel_button = Gtk.Button(label="Stop SSH Tunnel")
        stop_tunnel_button.connect("clicked", self.stop_ssh_tunnel)
        self.grid.attach(stop_tunnel_button, 1, 11, 2, 1)

        self.status_label = Gtk.Label()
        self.grid.attach(self.status_label, 0, 12, 3, 1)

        self.ssh_client = None
        self.tunnel_thread = None

    def browse_directory(self, button):
        dialog = Gtk.FileChooserDialog("Please choose a directory", self, Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.entry_directory.set_text(dialog.get_filename())
        dialog.destroy()

    def generate_ssh_keys(self, button):
        key_dir = self.entry_directory.get_text()
        custom_private_key_name = self.entry_custom_private_key_name.get_text()
        passphrase = self.entry_passphrase.get_text()
        key_length = int(self.key_length_combobox.get_active_text())
        key_type = self.key_type_combobox.get_active_text()

        if not key_dir:
            self.show_message("Error", "Please enter a directory path to save the keys.")
            return

        try:
            private_key_filename = os.path.join(key_dir, custom_private_key_name)
            public_key_filename = private_key_filename + ".pub"

            if os.path.exists(private_key_filename) or os.path.exists(public_key_filename):
                response = self.show_confirmation("Confirmation", "SSH keys already exist. Overwrite?")
                if not response:
                    return

            private_key = None
            if key_type == "RSA":
                private_key = paramiko.RSAKey.generate(key_length)
            elif key_type == "DSA":
                private_key = paramiko.DSSKey.generate(key_length)
            elif key_type == "ECDSA":
                private_key = paramiko.ECDSAKey.generate(key_length)

            if private_key:
                private_key.write_private_key_file(private_key_filename, password=passphrase)
                public_key = private_key.get_base64()
                with open(public_key_filename, 'w') as public_key_file:
                    public_key_file.write(public_key)

                self.show_message("Success", "SSH keys generated and saved successfully!")

        except Exception as e:
            self.show_message("Error", f"An error occurred: {str(e)}")

    def view_ssh_keys(self, button):
        key_dir = self.entry_directory.get_text()
        private_key_name = self.entry_custom_private_key_name.get_text()

        if not key_dir or not private_key_name:
            self.show_message("Error", "Please enter a directory path and private key name to view the keys.")
            return

        private_key_filename = os.path.join(key_dir, private_key_name)
        public_key_filename = private_key_filename + ".pub"

        if not os.path.exists(private_key_filename) or not os.path.exists(public_key_filename):
            self.show_message("Error", "The specified private key does not exist.")
            return

        private_key_content = self.read_file_contents(private_key_filename)
        public_key_content = self.read_file_contents(public_key_filename)

        view_window = Gtk.Window(title="View SSH Keys")
        view_window.maximize()  # Maximize the window to cover the entire screen

        private_key_label = Gtk.Label(label="Private Key:")
        private_key_textview = Gtk.TextView()
        private_key_textview.get_buffer().set_text(private_key_content)
        private_key_textview.set_editable(False)
        private_key_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        private_key_textview.override_font(Pango.FontDescription('Monospace'))
        private_key_scrolled_window = Gtk.ScrolledWindow()
        private_key_scrolled_window.set_hexpand(True)
        private_key_scrolled_window.set_vexpand(True)
        private_key_scrolled_window.add(private_key_textview)

        public_key_label = Gtk.Label(label="Public Key:")
        public_key_textview = Gtk.TextView()
        public_key_textview.get_buffer().set_text(public_key_content)
        public_key_textview.set_editable(False)
        public_key_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        public_key_textview.override_font(Pango.FontDescription('Monospace'))
        public_key_scrolled_window = Gtk.ScrolledWindow()
        public_key_scrolled_window.set_hexpand(True)
        public_key_scrolled_window.set_vexpand(True)
        public_key_scrolled_window.add(public_key_textview)

        grid = Gtk.Grid(column_spacing=10, row_spacing=10)
        grid.set_margin_top(20)
        grid.set_margin_left(20)
        grid.set_margin_right(20)
        grid.set_margin_bottom(20)
        grid.attach(private_key_label, 0, 0, 1, 1)
        grid.attach(private_key_scrolled_window, 0, 1, 1, 1)
        grid.attach(public_key_label, 0, 2, 1, 1)
        grid.attach(public_key_scrolled_window, 0, 3, 1, 1)

        view_window.add(grid)
        view_window.show_all()

    def read_file_contents(self, filename):
        try:
            with open(filename, 'r') as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def show_message(self, title, message):
        dialog = Gtk.MessageDialog(parent=self, flags=0, type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK,
                                   message_format=message)
        dialog.set_title(title)
        dialog.run()
        dialog.destroy()

    def show_confirmation(self, title, message):
        dialog = Gtk.MessageDialog(parent=self, flags=0, type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.YES_NO, message_format=message)
        dialog.set_title(title)
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES

    def start_ssh_tunnel(self, button):
        remote_host = self.entry_remote_host.get_text()
        remote_port = self.entry_remote_port.get_text()
        local_port = self.entry_local_port.get_text()

        if not remote_host or not remote_port or not local_port:
            self.show_message("Error", "Please enter remote host, remote port, and local port.")
            return

        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.load_system_host_keys()
            self.ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())

            # Use existing private key for authentication
            key_dir = self.entry_directory.get_text()
            private_key_name = self.entry_custom_private_key_name.get_text()
            private_key_path = os.path.join(key_dir, private_key_name)

            if not os.path.exists(private_key_path):
                self.show_message("Error", "Private key file does not exist.")
                return

            self.ssh_client.connect(remote_host, username=os.getlogin(), key_filename=private_key_path)

            self.tunnel_thread = threading.Thread(target=self.create_tunnel, args=(remote_port, local_port))
            self.tunnel_thread.start()

            self.show_message("Success", "SSH tunnel started successfully!")

        except Exception as e:
            self.show_message("Error", f"Failed to start SSH tunnel: {str(e)}")

    def create_tunnel(self, remote_port, local_port):
        try:
            transport = self.ssh_client.get_transport()
            transport.request_port_forward('localhost', int(local_port), ('localhost', int(remote_port)))
        except Exception as e:
            GObject.idle_add(self.show_message, "Error", f"Failed to create tunnel: {str(e)}")

    def stop_ssh_tunnel(self, button):
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
            if self.tunnel_thread and self.tunnel_thread.is_alive():
                self.tunnel_thread.join()
            self.show_message("Success", "SSH tunnel stopped successfully!")
        else:
            self.show_message("Error", "No active SSH tunnel to stop.")

win = SSHKeyGenerator()
win.show_all()
Gtk.main()

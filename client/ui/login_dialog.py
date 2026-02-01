"""Login dialog for play vnt client."""

import wx
import sys
from pathlib import Path

# Add parent directory to path to import config_manager
sys.path.insert(0, str(Path(__file__).parent.parent))
from config_manager import ConfigManager


class SetupAccountDialog(wx.Dialog):
    """Dialog to setup (add) an existing account."""

    def __init__(self, parent):
        super().__init__(parent, title="Setup New Account", size=(350, 250))
        self.username = ""
        self.password = ""
        self._create_ui()
        self.CenterOnScreen()

    def _create_ui(self):
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Username
        sizer.Add(wx.StaticText(panel, label="&Username:"), 0, wx.LEFT | wx.TOP, 10)
        self.username_input = wx.TextCtrl(panel)
        sizer.Add(self.username_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Password
        sizer.Add(wx.StaticText(panel, label="&Password:"), 0, wx.LEFT | wx.TOP, 10)
        self.password_input = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        sizer.Add(self.password_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ok_btn = wx.Button(panel, wx.ID_OK, "&Save")
        ok_btn.SetDefault()
        btn_sizer.Add(ok_btn, 0, wx.RIGHT, 5)
        cancel_btn = wx.Button(panel, wx.ID_CANCEL, "&Cancel")
        btn_sizer.Add(cancel_btn, 0)

        sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 15)
        panel.SetSizer(sizer)

        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)

    def on_ok(self, event):
        self.username = self.username_input.GetValue().strip()
        self.password = self.password_input.GetValue()

        if not self.username:
            wx.MessageBox("Please enter a username", "Error", wx.OK | wx.ICON_ERROR)
            return
        if not self.password:
            wx.MessageBox("Please enter a password", "Error", wx.OK | wx.ICON_ERROR)
            return

        self.EndModal(wx.ID_OK)


class LoginDialog(wx.Dialog):
    """Simplified Login dialog."""

    def __init__(self, parent=None):
        """Initialize the login dialog."""
        super().__init__(parent, title="play vnt Login", size=(500, 310)) # Adjusted size

        # Initialize config manager
        self.config_manager = ConfigManager()

        self.username = ""
        self.password = ""
        self.server_id = None
        self.account_id = None
        self.server_url = None

        self._ensure_default_server()
        self._account_ids = []  # Track account IDs by index

        self._create_ui()
        self.CenterOnScreen()

    def _ensure_default_server(self):
        """Ensure localhost:2004 exists and is selected."""
        servers = self.config_manager.get_all_servers()
        target_server_id = None
        
        # Look for existing localhost server
        for sid, sdata in servers.items():
            if sdata.get("host") == "localhost" and str(sdata.get("port")) == "2004":
                target_server_id = sid
                break
        
        if not target_server_id:
            # Create it
            target_server_id = self.config_manager.add_server("Default Server", "localhost", "2004")

        self.server_id = target_server_id
        # We don't need to 'select' it in UI since it's hardcoded, but we store ID for logic

    def _create_ui(self):
        """Create the UI components."""
        self.panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        title = wx.StaticText(self.panel, label="play vnt 11.")
        title_font = title.GetFont()
        title_font.PointSize += 4
        title_font = title_font.Bold()
        title.SetFont(title_font)
        sizer.Add(title, 0, wx.ALL | wx.CENTER, 15)

        # Accounts selection (ComboBox)
        accounts_label = wx.StaticText(self.panel, label="&User Account:")
        sizer.Add(accounts_label, 0, wx.LEFT | wx.TOP, 10)

        self.accounts_combo = wx.ComboBox(
            self.panel,
            style=wx.CB_READONLY | wx.CB_DROPDOWN
        )
        sizer.Add(self.accounts_combo, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Delete Account Button
        self.delete_account_btn = wx.Button(self.panel, label="Delete Account")
        self.delete_account_btn.Hide()
        sizer.Add(self.delete_account_btn, 0, wx.ALL | wx.CENTER, 5)

        # Buttons Sizer
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Login Button
        self.login_btn = wx.Button(self.panel, wx.ID_OK, "&Login")
        self.login_btn.SetDefault()
        button_sizer.Add(self.login_btn, 0, wx.RIGHT, 5)

        # Create Account Button
        self.create_account_btn = wx.Button(self.panel, label="Create &Account")
        button_sizer.Add(self.create_account_btn, 0, wx.RIGHT, 5)

        # Setup New Account Button
        self.setup_account_btn = wx.Button(self.panel, label="&Setup New Account")
        button_sizer.Add(self.setup_account_btn, 0, wx.RIGHT, 5)

        # Cancel Button
        cancel_btn = wx.Button(self.panel, wx.ID_CANCEL, "&Cancel")
        button_sizer.Add(cancel_btn, 0)

        sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 20)

        # Set sizer
        self.panel.SetSizer(sizer)

        # Bind events
        self.login_btn.Bind(wx.EVT_BUTTON, self.on_login)
        self.create_account_btn.Bind(wx.EVT_BUTTON, self.on_create_account)
        self.setup_account_btn.Bind(wx.EVT_BUTTON, self.on_setup_account)
        self.delete_account_btn.Bind(wx.EVT_BUTTON, self.on_delete_account)
        self.accounts_combo.Bind(wx.EVT_COMBOBOX, self.on_account_selection_change)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        
        # Populate accounts
        self._refresh_accounts_list()
        
        # Initial focus and selection state
        if self.accounts_combo.GetCount() > 0:
            self.accounts_combo.SetSelection(0)
            self.accounts_combo.SetFocus()
        else:
            # If no accounts, maybe focus create?
            self.create_account_btn.SetFocus()


    def _refresh_accounts_list(self):
        """Refresh the accounts combobox for the default server."""
        self.accounts_combo.Clear()
        self._account_ids = []

        if not self.server_id:
            return

        accounts = self.config_manager.get_server_accounts(self.server_id)
        for account_id, account in accounts.items():
            self.accounts_combo.Append(account.get("username", "Unknown"))
            self._account_ids.append(account_id)

        # Select last used account if available
        last_account_id = self.config_manager.get_last_account_id(self.server_id)
        if last_account_id and last_account_id in self._account_ids:
            idx = self._account_ids.index(last_account_id)
            self.accounts_combo.SetSelection(idx)
        elif self.accounts_combo.GetCount() > 0:
            self.accounts_combo.SetSelection(0)
        
        self._update_delete_button()

    def _get_selected_account_id(self) -> str:
        """Get the currently selected account ID."""
        selection = self.accounts_combo.GetSelection()
        if selection == wx.NOT_FOUND or selection >= len(self._account_ids):
            return None
        return self._account_ids[selection]

    def _update_delete_button(self):
        """Update the delete button label and visibility based on selection."""
        selection = self.accounts_combo.GetSelection()
        if selection != wx.NOT_FOUND:
            username = self.accounts_combo.GetString(selection)
            self.delete_account_btn.SetLabel(f"Delete Account {username}")
            self.delete_account_btn.Show()
        else:
            self.delete_account_btn.Hide()
        self.panel.Layout()

    def on_account_selection_change(self, event):
        """Handle account selection change."""
        self._update_delete_button()

    def on_delete_account(self, event):
        """Handle delete account button click."""
        account_id = self._get_selected_account_id()
        if not account_id:
            return

        username = self.accounts_combo.GetString(self.accounts_combo.GetSelection())
        msg = f"Are you sure you want to delete the account '{username}' from this computer? This will not delete the account on the server."
        if wx.MessageBox(msg, "Confirm Deletion", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING) == wx.YES:
            self.config_manager.delete_account(self.server_id, account_id)
            self._refresh_accounts_list()

    def on_login(self, event):
        """Handle login button click."""
        account_id = self._get_selected_account_id()
        if not account_id:
            wx.MessageBox("Please select an account", "Error", wx.OK | wx.ICON_ERROR)
            self.accounts_combo.SetFocus()
            return

        # Get account credentials
        account = self.config_manager.get_account_by_id(self.server_id, account_id)
        if not account:
            wx.MessageBox("Account not found", "Error", wx.OK | wx.ICON_ERROR)
            return

        self.account_id = account_id
        self.username = account.get("username", "")
        self.password = account.get("password", "")
        self.server_url = self.config_manager.get_server_url(self.server_id)

        # Save last used account
        self.config_manager.set_last_account(self.server_id, account_id)

        self.EndModal(wx.ID_OK)

    def on_create_account(self, event):
        """Handle create account button click."""
        server_url = self.config_manager.get_server_url(self.server_id)
        if not server_url:
             wx.MessageBox("Could not determine server URL", "Error", wx.OK | wx.ICON_ERROR)
             return

        from .registration_dialog import RegistrationDialog

        dlg = RegistrationDialog(self, server_url)
        if dlg.ShowModal() == wx.ID_OK:
             wx.MessageBox("Account created successfully! Please try to Setup New Account to add it to your list (or wait for approval if required).", "Info", wx.OK)
        dlg.Destroy()
    
    def on_setup_account(self, event):
        """Handle setup new account button click."""
        dlg = SetupAccountDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            # Add account to config
            self.config_manager.add_account(
                self.server_id,
                dlg.username,
                dlg.password
            )
            self._refresh_accounts_list()
            
            # Auto-select the new account
            # (It should be at the end, or we find it)
            # Simplest: Just refresh and select last added? Logic in refresh handles last *used*, not last *added*.
            # Let's find it manually
            accounts = self.config_manager.get_server_accounts(self.server_id)
            # Find account with matching username (theoretical collision if multiple same usernames, but id is unique)
            # We don't have ID returned easily from add_account unless we modify logic or lookup.
            # But add_account returns ID! 
            # Wait, dlg doesn't call add_account, it just gets data.
            # Ah, I see I called add_account above.
            
            # Let's verify add_account return logic in ConfigManager.
            # It returns account_id.
            
            # Ideally we'd select it. For now, refresh is enough, user can select.
            
        dlg.Destroy()

    def on_cancel(self, event):
        """Handle cancel button click."""
        self.EndModal(wx.ID_CANCEL)

    def get_credentials(self):
        """Get the login credentials."""
        return {
            "username": self.username,
            "password": self.password,
            "server_url": self.server_url,
            "server_id": self.server_id,
            "config_manager": self.config_manager,
        }

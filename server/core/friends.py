"""Friend system functionality for the PlayPalace server."""

import functools
from typing import TYPE_CHECKING

from ..users.network_user import NetworkUser
from ..users.base import MenuItem, EscapeBehavior, TrustLevel
from ..messages.localization import Localization

if TYPE_CHECKING:
    from ..persistence.database import Database


class FriendsMixin:
    """
    Mixin class providing friend system functionality.

    This mixin expects the following attributes on the class it's mixed into:
    - _db: Database instance
    - _users: dict[str, NetworkUser] of online users
    - _user_states: dict[str, dict] of user menu states
    - _show_main_menu(user): method to show main menu
    """

    _db: "Database"
    _users: dict[str, NetworkUser]
    _user_states: dict[str, dict]

    def _show_main_menu(self, user: NetworkUser) -> None:
        """Show main menu - to be implemented by the main class."""
        raise NotImplementedError

    # ==================== Menu Display Functions ====================

    def _show_friends_menu(self, user: NetworkUser) -> None:
        """Show the main friends menu."""
        items = [
            MenuItem(
                text=Localization.get(user.locale, "friend-list"),
                id="friend_list",
            ),
            MenuItem(
                text=Localization.get(user.locale, "friend-requests"),
                id="friend_requests",
            ),
            MenuItem(
                text=Localization.get(user.locale, "send-friend-request"),
                id="send_friend_request",
            ),
            MenuItem(text=Localization.get(user.locale, "back"), id="back"),
        ]
        user.show_menu(
            "friends_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "friends_menu"}

    def _show_friend_list_menu(self, user: NetworkUser) -> None:
        """Show the list of friends."""
        friends = self._db.get_friends(user.username)
        
        if not friends:
            user.speak_l("no-friends", buffer="activity")
            self._show_friends_menu(user)
            return

        items = []
        for friend_name in friends:
            # Check if online
            status = " (Online)" if friend_name in self._users else " (Offline)"
            items.append(MenuItem(text=friend_name + status, id=f"friend_{friend_name}"))
        
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        
        user.show_menu(
            "friend_list_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "friend_list_menu"}

    def _show_remove_friend_confirm_menu(self, user: NetworkUser, friend_name: str) -> None:
        """Show confirmation menu for removing a friend."""
        user.speak_l("remove-friend-confirm", player=friend_name)
        items = [
            MenuItem(text=Localization.get(user.locale, "confirm-yes"), id="yes"),
            MenuItem(text=Localization.get(user.locale, "confirm-no"), id="no"),
        ]
        user.show_menu(
            "remove_friend_confirm_menu",
            items,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "remove_friend_confirm_menu",
            "friend_name": friend_name,
        }

    def _show_friend_requests_menu(self, user: NetworkUser) -> None:
        """Show list of incoming friend requests."""
        requests = self._db.get_friend_requests(user.username)
        
        if not requests:
            items = [MenuItem(text=Localization.get(user.locale, "back"), id="back")]
            user.show_menu("friend_requests_menu", items)
        else:
            items = []
            for sender_name in requests:
                items.append(MenuItem(text=sender_name, id=f"request_{sender_name}"))
            items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
            
            user.show_menu(
                "friend_requests_menu",
                items,
                multiletter=True,
                escape_behavior=EscapeBehavior.SELECT_LAST,
            )
        
        self._user_states[user.username] = {"menu": "friend_requests_menu"}

    def _show_friend_request_actions_menu(self, user: NetworkUser, sender_name: str) -> None:
        """Show actions for a friend request (accept/reject)."""
        items = [
            MenuItem(text=Localization.get(user.locale, "accept"), id="accept"),
            MenuItem(text=Localization.get(user.locale, "reject"), id="reject"),
            MenuItem(text=Localization.get(user.locale, "back"), id="back"),
        ]
        user.show_menu(
            "friend_request_actions_menu",
            items,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "friend_request_actions_menu",
            "sender_name": sender_name,
        }

    def _show_send_friend_request_menu(self, user: NetworkUser) -> None:
        """Show menu to send a friend request."""
        items = [
            MenuItem(text=Localization.get(user.locale, "list-all-users"), id="list_users"),
            MenuItem(text=Localization.get(user.locale, "search-user"), id="search_user"),
            MenuItem(text=Localization.get(user.locale, "back"), id="back"),
        ]
        user.show_menu(
            "send_friend_request_menu",
            items,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "send_friend_request_menu"}

    def _show_all_users_for_friend_menu(self, user: NetworkUser) -> None:
        """Show list of all users to pick for friend request."""
        # Get all users except self
        cursor = self._db._conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username != ? ORDER BY username", (user.username,))
        users = [row["username"] for row in cursor.fetchall()]
        
        items = []
        for target_name in users:
            items.append(MenuItem(text=target_name, id=f"user_{target_name}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))
        
        user.show_menu(
            "list_all_users_friends_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "list_all_users_friends_menu"}

    def _show_search_user_editbox(self, user: NetworkUser) -> None:
        """Show editbox to enter username."""
        user.show_editbox(
            "search_friend_username",
            Localization.get(user.locale, "enter-username-prompt"),
        )
        self._user_states[user.username] = {"menu": "search_friend_editbox"}

    # ==================== Handler Functions ====================

    async def _handle_friends_menu_selection(self, user: NetworkUser, selection_id: str) -> None:
        if selection_id == "friend_list":
            self._show_friend_list_menu(user)
        elif selection_id == "friend_requests":
            self._show_friend_requests_menu(user)
        elif selection_id == "send_friend_request":
            self._show_send_friend_request_menu(user)
        elif selection_id == "back":
            self._show_main_menu(user)

    async def _handle_friend_list_selection(self, user: NetworkUser, selection_id: str) -> None:
        if selection_id == "back":
            self._show_friends_menu(user)
        elif selection_id.startswith("friend_"):
            friend_name = selection_id[7:]
            self._show_remove_friend_confirm_menu(user, friend_name)

    async def _handle_remove_friend_confirm_selection(self, user: NetworkUser, selection_id: str, state: dict) -> None:
        friend_name = state.get("friend_name")
        if selection_id == "yes" and friend_name:
            if self._db.remove_friend(user.username, friend_name):
                user.speak_l("friend-removed", player=friend_name)
                # Notify the friend if online
                if friend_name in self._users:
                    self._users[friend_name].speak_l("friend-removed", player=user.username)
            self._show_friend_list_menu(user)
        else:
            self._show_friend_list_menu(user)

    async def _handle_friend_requests_selection(self, user: NetworkUser, selection_id: str) -> None:
        if selection_id == "back":
            self._show_friends_menu(user)
        elif selection_id.startswith("request_"):
            sender_name = selection_id[8:]
            self._show_friend_request_actions_menu(user, sender_name)

    async def _handle_friend_request_actions_selection(self, user: NetworkUser, selection_id: str, state: dict) -> None:
        sender_name = state.get("sender_name")
        if not sender_name:
            self._show_friend_requests_menu(user)
            return

        if selection_id == "accept":
            if self._db.accept_friend_request(sender_name, user.username):
                user.speak_l("friend-request-accepted", player=sender_name)
                # Notify sender if online
                if sender_name in self._users:
                    self._users[sender_name].speak_l("friend-request-accepted", player=user.username)
                    self._users[sender_name].play_sound("online.ogg")
            self._show_friend_requests_menu(user)
        elif selection_id == "reject":
            self._db.reject_friend_request(sender_name, user.username)
            self._show_friend_requests_menu(user)
        else:
            self._show_friend_requests_menu(user)

    async def _handle_send_friend_request_selection(self, user: NetworkUser, selection_id: str) -> None:
        if selection_id == "list_users":
            self._show_all_users_for_friend_menu(user)
        elif selection_id == "search_user":
            self._show_search_user_editbox(user)
        elif selection_id == "back":
            self._show_friends_menu(user)

    async def _handle_list_all_users_friends_selection(self, user: NetworkUser, selection_id: str) -> None:
        if selection_id == "back":
            self._show_send_friend_request_menu(user)
        elif selection_id.startswith("user_"):
            target_name = selection_id[5:]
            await self._send_request_to(user, target_name)

    async def _handle_search_friend_username_input(self, user: NetworkUser, text: str) -> None:
        if not text:
            self._show_send_friend_request_menu(user)
            return
        
        # Check if user exists
        if not self._db.user_exists(text):
            user.speak_l("user-not-found", player=text)
            self._show_send_friend_request_menu(user)
            return
        
        await self._send_request_to(user, text)

    async def _send_request_to(self, user: NetworkUser, target_name: str) -> None:
        if target_name == user.username:
            user.speak_l("cannot-friend-self")
            self._show_send_friend_request_menu(user)
            return
        
        if self._db.are_friends(user.username, target_name):
            user.speak_l("already-friends", player=target_name)
            self._show_send_friend_request_menu(user)
            return
        
        if self._db.has_pending_request(user.username, target_name):
            user.speak_l("friend-request-already-sent", player=target_name)
            self._show_send_friend_request_menu(user)
            return
            
        # Check if they already sent US a request
        if self._db.has_pending_request(target_name, user.username):
             # Auto-accept
             self._db.accept_friend_request(target_name, user.username)
             user.speak_l("friend-request-accepted", player=target_name)
             if target_name in self._users:
                 self._users[target_name].speak_l("friend-request-accepted", player=user.username)
             self._show_friends_menu(user)
             return

        if self._db.add_friend_request(user.username, target_name):
            user.speak_l("friend-request-sent", player=target_name)
            
            # Notify target if online
            if target_name in self._users:
                self._users[target_name].speak_l("friend-request-received", player=user.username)
                self._users[target_name].play_sound("accountrequest.ogg")
            
            self._show_friends_menu(user)
        else:
            self._show_send_friend_request_menu(user)

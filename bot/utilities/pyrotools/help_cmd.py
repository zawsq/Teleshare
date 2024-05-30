from typing import ClassVar


class HelpCmd:
    """
    A class to manage help commands.

    Should only be used inside plugin files which execute on startup.
    """

    _helper: ClassVar[dict[str, dict[str, str | bool | list[str] | None]]] = {}

    @classmethod
    def set_help(  # noqa: PLR0913
        cls,
        command: str,
        description: str | None,
        allow_global: bool,  # noqa: FBT001
        allow_non_admin: bool,  # noqa: FBT001
        alias: str | list[str] = "N/A",
    ) -> None:
        """Set help information for a command.

        Parameters:
            command (str):
                The name of the command.

            alias (str | list[str] | None):
                The alias(es) of the command.

            description (str):
                The description of the command.

            allow_global (bool):
                Commands that can be  used by none admin if global mode is enabled in options.

            allow_non_admin (bool):
                Commands that is only available to non admin users and if global mode is disabled in option.


        Returns: None
        """
        cls._helper[command] = {
            "alias": alias,
            "description": description,
            "allow_global": allow_global,
            "allow_non_admin": allow_non_admin,
        }

    @classmethod
    def get_help(cls, command: str) -> dict[str, str | bool | list[str] | None] | None:
        """Get help information for a command.

        Parameters:
            command (str): The name of the command.

        Returns:
            dict: A dictionary containing the alias and description of the command.
        """
        return cls._helper.get(command)

    @classmethod
    def get_cmds(cls) -> list[str]:
        """Get a list of all commands.

        Returns:
            list: A list of all commands.
        """
        return list(cls._helper.keys())

    @classmethod
    def get_non_admin_cmds(cls) -> list[str]:
        """Get a list of non admin commands available to all subscribed users

        Returns:
            list: A list of allow_non_admin commands.
        """
        return [command for command, data in cls._helper.items() if data["allow_non_admin"]]

    @classmethod
    def get_global_cmds(cls) -> list[str]:
        """Get global commands that is usable if global mode is set enable in options

        Returns:
            list: A list of allow_global commands.
        """
        return [command for command, data in cls._helper.items() if data["allow_global"]]

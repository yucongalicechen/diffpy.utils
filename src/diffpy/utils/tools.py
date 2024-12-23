import importlib.metadata
import json
from copy import copy
from pathlib import Path


def clean_dict(obj):
    """
    Remove keys from the dictionary where the corresponding value is None.

    Parameters
    ----------
    obj: dict
        The dictionary to clean. If None, initialize as an empty dictionary.

    Returns
    -------
    dict:
        The cleaned dictionary with keys removed where the value is None.

    """
    obj = obj if obj is not None else {}
    for key, value in copy(obj).items():
        if not value:
            del obj[key]
    return obj


def stringify(obj):
    """
    Convert None to an empty string.

    Parameters
    ----------
    obj: str
        The object to convert. If None, return an empty string.

    Returns
    -------
    str or None:
        The converted string if obj is not None, otherwise an empty string.
    """
    return obj if obj is not None else ""


def load_config(file_path):
    """
    Load configuration from a .json file.

    Parameters
    ----------
    file_path: Path
        The path to the configuration file.

    Returns
    -------
    dict:
        The configuration dictionary or {} if the config file does not exist.

    """
    config_file = Path(file_path).resolve()
    if config_file.is_file():
        with open(config_file, "r") as f:
            config = json.load(f)
        return config
    else:
        return {}


def _sorted_merge(*dicts):
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged


def _create_global_config(args):
    username = input(
        f"Please enter the name you would want future work to be credited to " f"[{args.get('username', '')}]:  "
    ).strip() or args.get("username", "")
    email = input(f"Please enter the your email " f"[{args.get('email', '')}]:  ").strip() or args.get("email", "")
    return_bool = False if username is None or email is None else True
    with open(Path().home() / "diffpyconfig.json", "w") as f:
        f.write(json.dumps({"username": stringify(username), "email": stringify(email)}))
    print(
        f"You can manually edit the config file at {Path().home() / 'diffpyconfig.json'} using any text editor.\n"
        f"Or you can update the config file by passing new values to get_user_info(), "
        f"see examples here: https://www.diffpy.org/diffpy.utils/examples/toolsexample.html"
    )
    return return_bool


def get_user_info(owner_name=None, owner_email=None, owner_orcid=None):
    """
    Get name, email and orcid of the owner/user from various sources and return it as a metadata dictionary

    The function looks for the information in json format configuration files with the name 'diffpyconfig.json'.
    These can be in the user's home directory and in the current working directory.  The information in the
    config files are combined, with the local config overriding the home-directory one.  Values for
    owner_name, owner_email, and owner_orcid may be passed in to the function and these override the values
    in the config files.

    A template for the config file is below.  Create a text file called 'diffpyconfig.json' in your home directory
    and copy-paste the template into it, editing it with your real information.
    {
      "owner_name": "<your name as you would like it stored with your data>>",
      "owner_email": "<your_associated_email>>@email.com",
      "owner_orcid": "<your_associated_orcid if you would like this stored with your data>>"
    }
    You may also store any other gloabl-level information that you would like associated with your
    diffraction data in this file

    Parameters
    ----------
    owner_name: string, optional, default is the value stored in the global or local config file.
        The name of the user who will show as owner in the metadata that is stored with the data
    owner_email: string, optional, default is the value stored in the global or local config file.
        The email of the user/owner
    owner_name:  string, optional, default is the value stored in the global or local config file.
        The ORCID id of the user/owner

    Returns
    -------
    dict:
        The dictionary containing username, email and orcid of the user/owner, and any other information
        stored in the global or local config files.

    """
    runtime_info = {"owner_name": owner_name, "owner_email": owner_email, "owner_orcid": owner_orcid}
    for key, value in copy(runtime_info).items():
        if value is None or value == "":
            del runtime_info[key]
    global_config = load_config(Path().home() / "diffpyconfig.json")
    local_config = load_config(Path().cwd() / "diffpyconfig.json")
    # if global_config is None and local_config is None:
    #     print(
    #         "No global configuration file was found containing "
    #         "information about the user to associate with the data.\n"
    #         "By following the prompts below you can add your name and email to this file on the current "
    #         "computer and your name will be automatically associated with subsequent diffpy data by default.\n"
    #         "This is not recommended on a shared or public computer. "
    #         "You will only have to do that once.\n"
    #         "For more information, please refer to www.diffpy.org/diffpy.utils/examples/toolsexample.html"
    #     )
    user_info = global_config
    user_info.update(local_config)
    user_info.update(runtime_info)
    return user_info


def get_package_info(package_names, metadata=None):
    """
    Fetches package version and updates it into (given) metadata.

    Package info stored in metadata as {'package_info': {'package_name': 'version_number'}}.

    ----------
    package_name : str or list
        The name of the package(s) to retrieve the version number for.
    metadata : dict
        The dictionary to store the package info. If not provided, a new dictionary will be created.

    Returns
    -------
    dict:
        The updated metadata dict with package info inserted.

    """
    if metadata is None:
        metadata = {}
    if isinstance(package_names, str):
        package_names = [package_names]
    package_names.append("diffpy.utils")
    pkg_info = metadata.get("package_info", {})
    for package in package_names:
        pkg_info.update({package: importlib.metadata.version(package)})
    metadata["package_info"] = pkg_info
    return metadata

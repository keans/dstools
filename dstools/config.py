import os
import sys

try:
    # python2.7
    import ConfigParser as configparser
except:
    # python3
    import configparser


class Config(object):
    """
    config object for a simplified handling of config files
    """
    def __init__(self, filename, defaults=[], create_member_variables=False):
        self.filename = os.path.expanduser(filename)
        self.config = configparser.SafeConfigParser()

        if os.path.exists(self.filename):
            # load config from file, if it is existing
            self.load()

            if create_member_variables is True:
                # create member variables
                self._create_member_variables()

        elif len(defaults) > 0:
            # otherwise, set defaults, if provided
            self.set_defaults(defaults)
            sys.exit(
                "Please check the default config in '%s'!" % (
                    self.filename
                )
            )

    def _create_member_variables(self):
        """
        reads values of all sections from the config file
        and add it as member variables to the Config class
        """
        for section in self.config.sections():
            for k, v in self.config.items(section):
                if getattr(self, k, None) is None:
                    # new key => create member variable
                    setattr(self, k, v)

                else:
                    raise ValueError(
                        "cannot create member variable '{}' since not "
                        "unique".format(k)
                    )

    def set(self, section, key, value):
        """
        set a value in the config file in the given section
        under the given key
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)

    def get(self, section, key, type_=str):
        """
        get a value from a section by given key
        (type_ can be specified for cast)
        """
        if (
            not self.config.has_section(section) or
            not self.config.has_option(section, key)
        ):
            return None

        return type_(self.config.get(section, key))

    def save(self):
        """
        save the config to the config file
        """
        with open(self.filename, "w") as f:
            self.config.write(f)

    def load(self):
        """
        load the config from the config file
        """
        self.config.read(self.filename)

    def set_defaults(self, defaults, save=True):
        """
        sets given list of (section, key, value) triples as defaults
        """
        for item in defaults:
            if self.get(item[0], item[1]) is None:
                self.set(item[0], item[1], item[2])

        if save:
            self.save()

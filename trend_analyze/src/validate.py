class Validate:
    """
    This class generates validation for value stored in common model
    This validation is generated according to pyfields validator.
    """
    def generate(self, max_len=0, is_blank=False):
        """
        generate validation corresponding argument
        """
        validates = {}

        if max_len:
            k, v = self.__max_length(max_len)
            validates[k] = v

        if is_blank:
            k, v = self.__is_blank()
            validates[k] = v

        return validates

    @staticmethod
    def __max_length(length):
        """
        return validation for max length
        """
        return f"Specified value was too long. Max length is {length} characters", lambda x: len(x) <= length

    @staticmethod
    def __is_blank():
        """
        return validation for empty string
        White space and tab cannot include in validated string.
        """
        return "Specified value was blank. Cannot set blank String.", lambda x: bool(x) \
                                                                                and len(x) != 0 \
                                                                                and not x.isspace()

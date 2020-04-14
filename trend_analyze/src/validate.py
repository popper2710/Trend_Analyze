class Validate:
    def generate(self, max_len=0, is_blank=False):
        validates = {}

        if max_len:
            k, v = self.__max_length(max_len)
            validates[k] = v

        if is_blank:
            k, v = self.__check_empty()
            validates[k] = v

        return validates

    @staticmethod
    def __max_length(length):
        return f"Specified value was too long. Max length is {length} characters", lambda x: len(x) <= length

    @staticmethod
    def __check_empty():
        return "Specified value was empty. Cannot set empty String.", lambda x: not x or len(x) != 0

#!/usr/bin/python3


class DotNest:
    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, newdata):
        self._data = newdata

    def get(self, keys):
        """given a list of keys, return the value at spot

        keys must be a list/tuple of dict keys or ints for list elements"""
        keys = self.parse_keys(keys)
        ptr = self.data

        for n, k in enumerate(keys):
            if isinstance(ptr, list):
                if isinstance(k, str):
                    k = int(k)
                if len(ptr) <= k:
                    raise ValueError(f"list key #{n} int({k}) too large")
            if isinstance(ptr, dict) and k not in ptr:
                raise ValueError(f"key #{n} '{k}' not found in data")
            if ptr is None:
                return None
            ptr = ptr[k]

        return ptr

    def set(self, keys, value):
        "given a list of keys, set the value at that spot to a new value"
        keys = self.parse_keys(keys)
        ptr = self.get(keys[0:-1])
        ptr[keys[-1]] = value

    def parse_keys(self, values):
        if isinstance(values, list):
            return values
        # TODO: allow / pathing if values starts with a /?
        # TODO: deal with escapes
        return values.split(".")

    def __eq__(self, other):
        return self.deep_compare(self.data, other.data)

    # from https://stackoverflow.com/questions/25044073/comparing-python-objects-from-deepcopy
    def deep_compare(self, left, right, excluded_keys=[]):
        # convert left and right to dicts if possible, skip if they can't be converted
        try:
            left = left.__dict__
            right = right.__dict__
        except:
            pass

        # both sides must be of the same type
        if type(left) != type(right):
            return False

        # compare the two objects or dicts key by key
        if type(left) == dict:
            for key in left:
                # make sure that we did not exclude this key
                if key not in excluded_keys:
                    # check if the key is present in the right dict, if not, we are not equals
                    if key not in right:
                        return False
                    else:
                        # compare the values if the key is present in both sides
                        if not self.deep_compare(left[key], right[key], excluded_keys):
                            return False

            # check if any keys are present in right, but not in left
            for key in right:
                if key not in left and key not in excluded_keys:
                    return False

            return True

        # check for each item in lists
        if type(left) == list:
            # right and left must have the same length
            if len(left) != len(right):
                return False

            # compare each item in the list
            for index in range(len(left)):
                if not self.deep_compare(left[index], right[index], excluded_keys):
                    return False

        # do a standard comparison
        return left == right

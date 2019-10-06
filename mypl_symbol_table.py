class SymbolTable(object):
    """A symbol table consists of a stack of environments, where each
    environment maps a (variable) name to its associated information
    """
    def __init__(self):
        self.scopes = [] # list of {id_name:info}
        self.env_id = None # current environment in use

    def __get_env_index(self):
        for i, scope in enumerate(self.scopes):
            if self.env_id == id(scope):
                return i

    def __environment(self, name):
    # search from last (most recent) to first environment
        index = self.__get_env_index()
        for i in range(index, -1, -1):
            if name in self.scopes[i]:
                return self.scopes[i]

    def id_exists(self, identifier):
        return self.__environment(identifier) != None

    def id_exists_in_env(self, identifier, env_id):
        for scope in self.scopes:
            if env_id == id(scope):
                return identifier in scope

    def add_id(self, identifier):
        # can't add if no environments
        if not self.scopes:
            return
        # add to the current environment id
        self.scopes[self.__get_env_index()][identifier] = None

    def get_info(self, identifier):
        env = self.__environment(identifier)
        if env is not None:
            return env[identifier]

    def set_info(self, identifier, info):
        env = self.__environment(identifier)
        if env is not None:
            env[identifier] = info

    def push_environment(self):
        new_scope = {}
        if len(self.scopes) == 0:
            self.scopes.append(new_scope)
        else:
            index = self.__get_env_index()
            if index == len(self.scopes) - 1:
                self.scopes.append(new_scope)
            else:
                self.scopes.insert(index + 1, new_scope)
        self.env_id = id(new_scope)

    def get_env_id(self):
        return self.env_id

    def set_env_id(self, env_id):
        self.env_id = env_id

    def pop_environment(self):
        if len(self.scopes) <= 0:
            return
        index = self.__get_env_index()
        del self.scopes[index]
        if index > 0:
            self.env_id = id(self.scopes[index - 1])
        else:
            self.env_id = None

    def __str__(self):
        s = ''
        for i, scope in enumerate(self.scopes):
            s += ' '*i + str(id(scope)) + ': ' + str(scope) + '\n'
        return s
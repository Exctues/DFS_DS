class FSTree:
    def __init__(self):
        self.__root = self.__RootNode()

    def insert(self, path, size=-1, ip_address_pool=None):
        path = path.split('/')
        print(path)
        path = list(filter(lambda path: path != '', path))
        curr = self.__root

        for node_name in path[:-1]:
            child = curr.get_child(node_name)
            if not child:
                child = self.DirNode(node_name, curr)

            curr = child

        if size < 0:
            # Creating dir
            print(path)
            child = self.DirNode(path[-1], curr)
        else:
            child = self.FileNode(path[-1], curr, size, ip_address_pool)

        return child

    def find_node(self, path):

        path = path.split('/')
        path = filter(lambda path: path != '', path)
        curr = self.__root

        for name in path:
            curr = curr.get_child(name)
            if curr is None:
                return curr

        return curr

    def remove(self, path):
        node = self.find_node(path)
        if node is None:
            return None
        return node.erase()

    # Debugging
    def print_tree(self, level=-1, node=None):
        if node is None:
            node = self.__root

        if level >= 0:
            text = '\t' * level
            if level == 0:
                text += '/'

            text += repr(node)

            if node.is_dir:
                text += '/'

            print(text)

        for child in node.children:
            if child.name != '..' and child.name != '.':
                self.print_tree(level + 1, child)

    class FSNode:
        def __init__(self, name, parent):
            self.children = []
            self.__name = name.strip('/')
            self.parent = parent
            self.is_dir = True

            if parent is not None:
                parent.children.append(self)

        @property
        def name(self):
            return self.__name

        def get_path(self) -> str:
            if self.parent is None:
                return self.name

            res = self.parent.get_path() + '/' + self.name
            res = '/' + res.strip('/')

            return res

        def get_child(self, name):
            if name == '.':
                return self
            if name == '..':
                return self.parent

            for child in self.children:
                if child.name == name:
                    return child

            return None

        def get_children(self):
            return [repr(child) for child in self.children]

        def erase(self):
            self.parent.children.remove(self)
            del self
            return True

        def __repr__(self):
            return self.name

        def __str__(self):
            return self.get_path()

    class DirNode(FSNode):
        def __init__(self, name, parent=None):
            super().__init__(name, parent)
            self.__add_default_dirs()

        def __add_default_dirs(self):
            two_dots = FSTree.FSNode('..', self)
            two_dots.children = self.parent.children

            one_dot = FSTree.FSNode('.', self)
            one_dot.children = self.children

    class FileNode(FSNode):
        def __init__(self, name, parent, size, ip_addresses_pool=None):
            if parent is None:
                print("A file must be in a directory")
                return

            if ip_addresses_pool is None:
                ip_addresses_pool = []

            super().__init__(name, parent)
            self.ip_pool = ip_addresses_pool
            self.__size = size
            self.is_dir = False

        @property
        def size(self):
            return self.__size

        def __str__(self):
            # return str(self.get_path())+' ('+str(self.size)+' bytes)'
            return "{} ({} bytes)".format(self.get_path(), self.size)

    class __RootNode(FSNode):
        def __init__(self):
            super().__init__('/', None)

        def get_path(self):
            return '/'

        def __repr__(self):
            return '/'

        def __str__(self):
            return '/'

        def erase(self):
            for child in self.children:
                child.erase()

            self.children = []
            return True

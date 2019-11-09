import pprint


class FSTree:
    def __init__(self):
        self.__root = self.DirNode('/')

    def insert(self, path, size=-1, ip_address_pool=None):
        path = path.split('/')
        path = list(filter(lambda path: path != '', path))
        curr = self.__root

        for node_name in path[:-1]:
            child = curr.get_child(node_name)
            if not child:
                child = self.DirNode(node_name, curr)

            curr = child

        if size < 0:
            # Creating dir
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
        def __init__(self, name, parent=None):
            self.children = []
            self.__name = name.strip('/')
            self.parent = parent
            self.is_dir = True

            if parent is not None:
                parent.children.append(self)

        @property
        def name(self):
            return self.__name

        def get_path(self):
            if self.parent is None:
                return self.name

            res = self.parent.get_path() + '/' + self.name
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

        def __repr__(self):
            return self.name

        def __str__(self):
            return self.get_path()

    class DirNode(FSNode):
        def __init__(self, name, parent=None):
            if name == '/' and parent:
                print("Name cannot be empty!")
                return
            elif not parent and name != '/':
                print("Parent directory is not specified!")
                return

            if not parent:
                self.is_root = True
            else:
                self.is_root = False

            super().__init__(name, parent)
            if not self.is_root:
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

        def __repr__(self):
            return f"{self.get_path()} ({self.size} bytes) [{', '.join(self.ip_pool)}]"


if __name__ == '__main__':
    ip_addresses = ['192.168.0.1', '192.168.0.10', '127.0.0.1']

    tree = FSTree()
    tree.insert('/dev')
    tree.insert('/var')
    tree.insert('/home')
    tree.insert('/home/daniel')
    tree.insert('/home/alex')
    tree.insert('/home/daniel/prog.py', 1000, ip_addresses)
    tree.insert('/home/daniel/config.ini', 10)

    node = tree.find_node('/home/daniel/../alex/')
    print(node, end='\n'*2)

    tree.print_tree()

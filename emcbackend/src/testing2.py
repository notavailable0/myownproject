class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        current = self.root
        for char in word:
            node = current.children.get(char)
            if node is None:
                node = TrieNode()
                current.children[char] = node
            current = node
        current.is_end_of_word = True

    def search(self, word):
        current = self.root
        for char in word:
            node = current.children.get(char)
            if node is None:
                return False
            current = node
        return current.is_end_of_word

    def starts_with(self, prefix):
        current = self.root
        words = []
        for char in prefix:
            node = current.children.get(char)
            if node is None:
                return words
            current = node
        self._dfs(current, prefix, words)
        return words

    def _dfs(self, node, prefix, words):
        if node.is_end_of_word:
            words.append(prefix)
        for char, child_node in node.children.items():
            self._dfs(child_node, prefix + char, words)


testdict = ['hello', 'working', 'sleeping', 'eating', 'eatingea']
trie = Trie()
for i in testdict:
    trie.insert(i)

print(trie.starts_with("eat"))
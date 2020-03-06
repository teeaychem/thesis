print("Hi")


class Node:

    kinds = ["choice", "outcome", "decorative"]

    def __init__(self, name, parent, kind):
        self.name = name
        self.parent = parent
        self.kind = kind
        self.children = []
        self.utility = 0
        self.probability = 1

    def addChild(self, nodearg):
        if nodearg.name == self.name:
            print("No way!")
        else:
            self.children.append(nodearg)

    def checkChildren(self):
        if len(self.children) > 0:
            probSum = 0
            for child in self.children:
                probSum += child.probability

    def normaliseChildren(self):
        probSum = 0
        for child in self.children:
            probSum += child.probability
        for child in self.children:
            child.probability = child.probability/probSum



class Instance:

    def __init__(self):
        self.initialNode = Node("start", "", "decorative")

    # def addNode(self, node, parent):
    #

    def findNode(self, name):
        result = self.findNodeHelper(self.initialNode, name)
        if result:
            print("found")
        return result

    def findNodeHelper(self, node, argname):
        if node.name == argname:
            return node
        elif len(node.children) > 0:
            for child in node.children:
                result = self.findNodeHelper(child, argname)
                if result:
                    return result
        else:
            return False

    def addNode(self, node):
        parent = self.findNode(node.parent)
        if parent:
            parent.addChild(node)
            print("added " + node.name + " to " + parent.name)
        else:
            print("parent not found")

    def print(self):
        self.printHelper(self.initialNode, 0)

    def printHelper(self, node, indent):
        print(" " * indent + "|" + node.name + " => (u: " + str(node.utility) + ", p: " + str(node.probability) +")" )
        if len(node.children) > 0:
            for child in node.children:
                self.printHelper(child, indent + 1)




test = Instance()
test.findNode("start")
test.addNode(Node("x", "start", "decorative"))
test.addNode(Node("y", "start", "decorative"))
test.findNode("start").normaliseChildren()
# test.addNode(Node("z", "x", "decorative"))
# test.addNode(Node("t", "x", "decorative"))
test.print()
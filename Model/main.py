import random
import numpy as np
import matplotlib.pyplot as plt

print("Hi")


class Node:

    kinds = ["choiceOutcome", "choicePoint", "outcome", "decorative"]

    def __init__(self, name, parent, kind, credence, utility, probability):
        self.name = name
        self.parent = parent
        self.kind = kind
        self.children = []
        self.probability = probability
        self.credence = credence
        self.utility = utility

    def addChild(self, nodearg):
        self.children.append(nodearg)

    def checkChildren(self):
        if len(self.children) > 0:
            credSum = 0
            for child in self.children:
                credSum += child.credence

    def normaliseChildren(self):
        credSum = 0
        for child in self.children:
            credSum += child.credence
        for child in self.children:
            child.credence = child.credence/credSum


class Instance:

    def __init__(self):
        self.initialNode = Node("start", "", "decorative", 1, 0, 1)
        self.iteration = 1
        self.history = []

    def findNode(self, name):
        result = self.findNodeHelper(self.initialNode, name)
        # if result:
        #     print("found")
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
            return None

    def addNode(self, node):
        parent = self.findNode(node.parent)
        if parent is not None:
            parent.addChild(node)
            print("added " + node.name + " to " + parent.name)
        else:
            print("parent not found")

    def print(self):
        self.printHelper(self.initialNode, 0)

    def printHelper(self, node, indent):
        print(" " * indent + "|" + node.name + " => (u: " + str(node.utility) + ", c: " + str(node.credence) + ", p: " + str(node.probability) + ")" )
        if len(node.children) > 0:
            for child in node.children:
                self.printHelper(child, indent + 1)

    def calcEUName(self, nodeName):

        startNode = self.findNode(nodeName)
        table = []
        self.calcEUHelper(startNode, 1, table)
        EU = 0
        for item in table:
            EU += item[1][0] * item[1][1]
        print(EU)
        return table

    def calcEUNode(self, node):
        table = []
        self.calcEUHelper(node, 1, table)
        EU = 0
        for item in table:
            EU += item[1][0] * item[1][1]
        return EU
        # return table

    def calcEUHelper(self, startNode, currentCredence, table):
        if len(startNode.children) == 0:
            table.append([startNode.name, [currentCredence, startNode.utility]])
        else:
            for child in startNode.children:
                self.calcEUHelper(child, currentCredence * child.credence, table)

    def updateStatesOfNatureFromNode(self, startNode, iteration):
        self.updateStatesOfNatureFromNodeHelper(startNode, startNode.credence, iteration)
        self.normaliseAllNodes()

    def updateStatesOfNatureFromNodeHelper(self, startNode, totalCredence, iteration):
        if startNode.kind == "outcome":
            # Increasing iteration should reduce variance
            variance = abs(startNode.probability - startNode.credence) / (.001 * iteration)
            # Currently this enforces that probability and credences are always fairly well aligned
            startNode.credence = random.uniform(max(0, startNode.probability - variance), min(1, startNode.probability + variance))
        else:
            for child in startNode.children:
                # Only change credence with choice, not outcome
                newCredence = startNode.credence
                if startNode.kind == "choiceOutcome":
                    newCredence = newCredence * startNode.credence
                self.updateStatesOfNatureFromNodeHelper(child, newCredence, iteration)

    def normaliseAllNodes(self):
        self.normaliseNodesHelper(self.initialNode)

    def normaliseNodesHelper(self, node):
        node.normaliseChildren()
        for child in node.children:
            self.normaliseNodesHelper(child)

    def simpleUpdateNode(self, node):

        if len(node.children) > 0:

            update = False
            childEU = []

            for child in node.children:
                childEU.append(self.simpleUpdateNode(child))
                if child.kind == "choiceOutcome":
                    update = True
            statusQuo = sum(childEU)
            # for index in range(len(childEU)):
            #     print("cr: ", node.children[index].credence)
            #     statusQuo += node.children[index].credence * childEU[index]

            if update:
                # print("Updating", node.name)
                # print("SQ", statusQuo)
                # If updating, then adjust credence in choices
                childCov = []
                for index in range(len(childEU)):
                    childCov.append(max(0, (childEU[index]/node.children[index].credence) - statusQuo))   #self.cov(childEU[index], statusQuo))
                    # print("childEU", childEU[index])
                    # print("childCov", max(0, (childEU[index]/node.children[index].credence) - statusQuo))
                covSum = sum(childCov)
                # print("childEU", childEU)
                # print("childCov", childCov)
                # print("CS", covSum)

                for childIndex in range(len(childEU)):
                    # print("changing: ", node.children[childIndex].name)
                    # print("from: ", node.children[childIndex].credence)
                    childCredence = node.children[childIndex].credence
                    node.children[childIndex].credence = (childCredence + childCov[childIndex])/(1 + covSum)
                    # print((childCredence + childCov[childIndex])/(1 + covSum))
                    # print("to: ", node.children[childIndex].credence)
                # Now credences are updated, recalculate EU of current node
                # print(node.children)
                # print(childIndex)
                # print(node.children[childIndex])
                return node.credence * self.calcEUNode(node.children[childIndex])

            else:
                # Else, the statusQuo is the same as the EU
                return node.credence * statusQuo

        else:
            # If no children, then calculate the EU of the terminal point
            return node.credence * node.utility

    def simpleUpdate(self, iterations):
        for i in range(0, iterations):
            self.updateStatesOfNatureFromNode(test.findNode("start"), self.iteration)
            self.simpleUpdateNode(self.initialNode)
            self.iteration += 1
            self.print()
            self.history.append(self.calculateTotalCredences())

    def getNodes(self):
        list = []
        self.addSubNodeNamesToList(self.initialNode, list)
        return list

    def addSubNodeNamesToList(self, node, list):
        list.append(node.name)
        for child in node.children:
            self.addSubNodeNamesToList(child, list)

    def calculateTotalCredences(self):
        list = []
        self.calculateTotalCredencesHelper(self.initialNode, 1, list)
        return list

    def calculateTotalCredencesHelper(self, node, credence, list):
        list.append(node.credence * credence)
        for child in node.children:
            self.calculateTotalCredencesHelper(child, credence * node.credence, list)

    def getHistory(self):
        histList = []
        for name in self.getNodes():
            histList.append([name])
        for line in self.history:
            for index in range(len(histList)):
                histList[index].append(line[index])
        return histList

    def sampleFromHistory(self, step):
        histList = []
        for name in self.getNodes():
            histList.append([name])
        for lineIndex in range(0, len(self.history), step):
            for index in range(len(histList)):
                histList[index].append(self.history[lineIndex][index])
        return histList



test = Instance()
test.findNode("start")
test.addNode(Node("x", "start", "choiceOutcome", .7, 0, .7))
test.addNode(Node("x2", "x", "outcome", 1, 3, 1))
test.addNode(Node("y", "start", "choiceOutcome", .3, 0, .3))
test.addNode(Node("a", "y", "outcome", 0.5, 7.5, 0.2))
test.addNode(Node("b", "y", "outcome", 0.5, 2, 0.8))
test.findNode("start").normaliseChildren()
# test.addNode(Node("z", "x", "decorative"))
# test.addNode(Node("t", "x", "decorative"))
test.print()
# print(test.calcEUName("start"))
# print(test.calcEUName("x"))
# print(test.calcEUName("y"))
# test.updateStatesOfNatureFromNode(test.findNode("start"))
print("Before")
test.print()
test.simpleUpdate(100)
print("After")
test.print()
print(test.getNodes())
print(test.calculateTotalCredences())
print(test.getHistory())

# xdata = np.random.random([2, 10])
# print(xdata)




fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

testHistory = test.sampleFromHistory(5)

legend = []
for index in range(len(testHistory)):
    legend.append(testHistory[index][0])
    ydata = testHistory[index][1:]
    ax.plot([i for i in range(len(testHistory[index][1:]))], testHistory[index][1:], label=testHistory[index][0])

plt.legend(legend, loc=4)
ax.set_xlim([0, len(testHistory[index][1:])])
ax.set_ylim([0, 1])
ax.set_title('Example')
plt.show()
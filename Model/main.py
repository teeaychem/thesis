import random
import numpy as np
import matplotlib.pyplot as plt
import math

print("Hello!")


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
        self.step = 0.25
        self.history = []

    def findNode(self, name):
        result = self.findNodeHelper(self.initialNode, name)
        if result:
            return result

    def findNodeHelper(self, node, argName):
        if node.name == argName:
            return node
        elif len(node.children) > 0:
            for child in node.children:
                result = self.findNodeHelper(child, argName)
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
            # Increasing iteration should reduce distance
            distance = startNode.probability - startNode.credence
            newCredence = startNode.credence + (distance/(iteration*10))*startNode.credence # random.uniform(max(0,(1/distance)), min(1,1/distance))
            # Currently this enforces that probability and credences are always fairly well aligned
            startNode.credence = newCredence

                 # (startNode.probability + (math.sin(iteration/10)))
                                                           #random.uniform(max(0, startNode.probability - distance), min(1, startNode.probability + distance))))
            #random.uniform(max(0, startNode.probability - distance), min(1, startNode.probability + distance))
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

            if update:
                # If updating, then adjust credence in choices
                childCov = []
                for index in range(len(childEU)):
                    childCov.append(max(0, (childEU[index]/node.children[index].credence) - statusQuo))
                covSum = sum(childCov)

                for childIndex in range(len(childEU)):
                    childCredence = node.children[childIndex].credence
                    node.children[childIndex].credence = (childCredence + childCov[childIndex])/(1 + covSum)
                # Now credences are updated, recalculate EU of current node
                return node.credence * self.calcEUNode(node.children[childIndex])

            else:
                # Else, the statusQuo is the same as the EU
                return node.credence * statusQuo

        else:
            # If no children, then calculate the EU of the terminal point
            return node.credence * node.utility

    def simpleUpdate(self, iterations):
        for i in range(0, iterations):
            # 1. 'process information'
            self.updateStatesOfNatureFromNode(test.findNode("start"), self.iteration)
            # 2. update nodes 'from ends to means'
            self.simpleUpdateNode(self.initialNode)
            self.iteration += self.step
            self.history.append(self.calculateTotalCredences())

    def getNodes(self):
        nodeList = []
        self.addSubNodeNamesToList(self.initialNode, nodeList)
        return nodeList

    def addSubNodeNamesToList(self, node, list):
        list.append(node.name)
        for child in node.children:
            self.addSubNodeNamesToList(child, list)

    def calculateTotalCredences(self):
        credenceList = []
        self.calculateTotalCredencesHelper(self.initialNode, 1, credenceList)
        return credenceList

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
        for name in self.getNodes()[1:]:
            histList.append([name])
        for lineIndex in range(1, len(self.history), step):
            for index in range(len(histList)):
                histList[index].append(self.history[lineIndex][index + 1])
        return histList

    def plotHistory(self, step):

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        # https://matplotlib.org/3.1.0/tutorials/colors/colormaps.html for colour maps
        cmap = plt.cm.get_cmap(plt.cm.rainbow, 1000)

        testHistory = self.sampleFromHistory(step)

        legend = []
        for index in range(len(testHistory)):
            legend.append(testHistory[index][0])
            ax.plot([i for i in range(len(testHistory[index][1:]))], testHistory[index][1:],
                    label=testHistory[index][0], color=cmap(index*20))

        plt.legend(legend, loc=0)
        ax.set_xlim([0, len(testHistory[0][1:])])
        ax.set_ylim([0, 1])
        ax.set_title('Example')
        plt.show()


test = Instance()
test.findNode("start")
test.addNode(Node("neighbour", "start", "choiceOutcome", .7, 0, .7))
test.addNode(Node("nHas", "neighbour", "outcome", .7, 4, .1))
test.addNode(Node("~nHas", "neighbour", "outcome", .3, -6, .9))
test.addNode(Node("shops", "start", "choiceOutcome", .3, 0, .3))
test.addNode(Node("supermarket", "shops", "choiceOutcome", 0.5, 0, 0.8))
test.addNode(Node("smHas", "supermarket", "outcome", 0.5, 3, 0.8))
test.addNode(Node("~smHas", "supermarket", "outcome", 0.5, -4, 0.2))
test.addNode(Node("market", "shops", "choiceOutcome", 0.5, 0, 0.2))
test.addNode(Node("mHas", "market", "outcome", 0.5, 4, 0.4))
test.addNode(Node("~mHas", "market", "outcome", 0.5, -3, 0.6))
test.addNode(Node("organic", "shops", "choiceOutcome", 0.1, 0, 0.2))
test.addNode(Node("oHas", "organic", "outcome", 0.5, 6, 0.3))
test.addNode(Node("~oHas", "organic", "outcome", 0.5, -7, 0.7))
test.print()
# print(test.calcEUName("start"))
# print(test.calcEUName("x"))
# print(test.calcEUName("y"))
# test.updateStatesOfNatureFromNode(test.findNode("start"))

test.simpleUpdate(100)
test.plotHistory(1)

# xdata = np.random.random([2, 10])
# print(xdata)





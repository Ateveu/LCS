import pandas as pd

class Node:
    def __init__(self, value, parent):
        self.value = value
        self.parent = parent
        self.children = []
    def addChild(self, index):
        self.children.append(index)
    def truthValue(self, tree, d, a):
        if self.value == '!':
            t = tree[self.children[0]].truthValue(tree, d, a)
            prop = '(!' + t[0] + ')'
            ans = not t[1]
            d.update(t[2])
            if prop not in d:
                d.update({prop: [ans]})
            else:
                ans = d[prop][0]
            return (prop, ans, d)
        elif self.value in ['&', '|', '=', '<', '>']:
            t1 = tree[self.children[0]].truthValue(tree, d, a)
            d.update(t1[2])
            t2 = tree[self.children[1]].truthValue(tree, d, a)
            d.update(t2[2])
            prop = '(' + t1[0] + self.value + t2[0] + ')'
            if self.value == '&':
                ans = t1[1] and t2[1]
            elif self.value == '|':
                ans = t1[1] or t2[1]
            elif self.value == '=':
                ans = t1[1] == t2[1]
            elif self.value == '>':
                if t1[1] == True and t2[1] == False:
                    ans = False
                else:
                    ans = True
            elif self.value == '<':
                if t2[1] == True and t1[1] == False:
                    ans = False
                else:
                    ans = True
            else:
                ans = ''
            if prop not in d:
                d.update({prop: [ans]})
            else:
                ans = d[prop][0]
            return (prop, ans, d)
        elif self.value.isupper():
            ans = a[self.value]
            if self.value not in d:
                d.update({self.value: [ans]})
            else:
                ans = d[self.value]
            return (self.value, ans, d)

class TreeProp:
    def __init__(self, p, relaxed = False):
        self.prop = p
        self.nodes = []
        self.leaves = []
        if relaxed == True:
            p = self.unrelax(p)
            print(p)
        s = 0
        connectives = []
        self.atomics = []
        for i in range(len(p)):
            print(i, p[i])
            if s == 0:
                if p[i] == '(':
                    self.nodes.append(Node('"c"', -1))
                    print(self.getNode(0))
                    connectives.append(0)
                    s = 1
                elif p[i].isalpha():
                    self.nodes.append(Node(p[i], -1))
                    print(self.getNode(0))
                    self.leaves.append(self.lastNode())
                    if p[i] not in self.atomics:
                        self.atomics.append(p[i])
                    s = 2
            elif s == 1:
                if p[i] == '(':
                    par = self.lastNode()
                    self.nodes.append(Node('"c"', connectives[-1]))
                    print(self.getNode(self.lastNode()))
                    self.nodes[par].addChild(self.lastNode())
                    connectives.append(self.lastNode())
                    s = 1
                elif p[i] == '!':
                    self.nodes[connectives[-1]].value = '!'
                    print(self.getNode(connectives[-1]))
                    s = 4
                elif p[i].isalpha():
                    self.nodes.append(Node(p[i], connectives[-1]))
                    print(self.getNode(self.lastNode()))
                    self.nodes[connectives[-1]].addChild(self.lastNode())
                    self.leaves.append(self.lastNode())
                    if p[i] not in self.atomics:
                        self.atomics.append(p[i])
                    s = 3
            elif s == 3:
                if p[i] in ['&', '|', '=', '<', '>']:
                    self.nodes[connectives[-1]].value = p[i]
                    print(self.getNode(connectives[-1]))
                    s = 4
            elif s == 4:
                if p[i].isalpha():
                    self.nodes.append(Node(p[i], connectives[-1]))
                    print(self.getNode(self.lastNode()))
                    self.nodes[connectives[-1]].addChild(self.lastNode())
                    self.leaves.append(self.lastNode())
                    if p[i] not in self.atomics:
                        self.atomics.append(p[i])
                    s = 5
                elif p[i] == '(':
                    self.nodes.append(Node('"c"', connectives[-1]))
                    print(self.getNode(self.lastNode()))
                    self.nodes[connectives[-1]].addChild(self.lastNode())
                    connectives.append(self.lastNode())
                    s = 1
            elif s == 5:
                if p[i] == ')':
                    del connectives[-1]
                    s = 6
            elif s == 6:
                if p[i] in ['&', '|', '=', '<', '>']:
                    self.nodes[connectives[-1]].value = p[i]
                    print(self.getNode(connectives[-1]))
                    s = 4
                elif p[i] == ')':
                    del connectives[-1]
                    s = 6
            elif s == 2:
                print('ha?')
    def unrelax(self, p):
        while '!' in p:
            for i in range(0, len(p)):
                if p[i] == '!':
                    if p[i + 1].isupper():
                        s = list(p)
                        s[i] = '(a'
                        s[i + 1] = s[i + 1] + ')'
                        p = ''.join(s)
                        break
                    elif p[i + 1] == '(':
                        s = list(p)
                        s[i] = '(a'
                        c = 0
                        for j in range(i, len(s)):
                            if s[j] == '(':
                                c += 1
                            elif s[j] == ')':
                                c -= 1
                                if c == 0:
                                    s[j] = '))'
                                    break
                        p = ''.join(s)
                        break
        p = p.replace('a', '!')
        while '|' in p or '&' in p:
            for i in range(0, len(p)):
                s = list(p)
                if p[i] in ['|', '&']:
                    if p[i] == '|':
                        s[i] = 'a'
                    else:
                        s[i] = 'b'
                    if p[i - 1].isupper():
                        s[i - 1] = '(' + p[i - 1]
                    elif p[i - 1] == ')':
                        c = 0
                        for j in range(i, -1):
                            if s[j] == ')':
                                c += 1
                            elif s[j] == '(':
                                c -= 1
                                if c == 0:
                                    s[j] = '(('
                                    break
                    if p[i + 1].isupper():
                        s[i + 1] = p[i + 1] + ')'
                        p = ''.join(s)
                        break
                    elif p[i + 1] == '(':
                        c = 0
                        for j in range(i, len(s)):
                            if s[j] == '(':
                                c += 1
                            elif s[j] == ')':
                                c -= 1
                                if c == 0:
                                    s[j] = '))'
                                    break
                        p = ''.join(s)
                        break
        p = p.replace('a', '|')
        p = p.replace('b', '&')
        while '<' in p or '>' in p:
            for i in range(0, len(p)):
                s = list(p)
                if p[i] in ['<', '>']:
                    if p[i] == '<':
                        s[i] = 'a'
                    else:
                        s[i] = 'b'
                    if p[i - 1].isupper():
                        s[i - 1] = '(' + p[i - 1]
                    elif p[i - 1] == ')':
                        c = 0
                        for j in range(i, -1):
                            if s[j] == ')':
                                c += 1
                            elif s[j] == '(':
                                c -= 1
                                if c == 0:
                                    s[j] = '(('
                                    break
                    if p[i + 1].isupper():
                        s[i + 1] = p[i + 1] + ')'
                        p = ''.join(s)
                        break
                    elif p[i + 1] == '(':
                        c = 0
                        for j in range(i, len(s)):
                            if s[j] == '(':
                                c += 1
                            elif s[j] == ')':
                                c -= 1
                                if c == 0:
                                    s[j] = '))'
                                    break
                        p = ''.join(s)
                        break
        p = p.replace('a', '<')
        p = p.replace('b', '>')
        while '=' in p:
            for i in range(0, len(p)):
                s = list(p)
                if p[i] == '=':
                    s[i] = 'a'
                    if p[i - 1].isupper():
                        s[i - 1] = '(' + p[i - 1]
                    elif p[i - 1] == ')':
                        c = 0
                        for j in range(i, -1):
                            if s[j] == ')':
                                c += 1
                            elif s[j] == '(':
                                c -= 1
                                if c == 0:
                                    s[j] = '(('
                                    break
                    if p[i + 1].isupper():
                        s[i + 1] = p[i + 1] + ')'
                        p = ''.join(s)
                        break
                    elif p[i + 1] == '(':
                        c = 0
                        for j in range(i, len(s)):
                            if s[j] == '(':
                                c += 1
                            elif s[j] == ')':
                                c -= 1
                                if c == 0:
                                    s[j] = '))'
                                    break
                        p = ''.join(s)
                        break
        p = p.replace('a', '=')
        return p
    def lastNode(self):
        return len(self.nodes) - 1
    def getNode(self, i):
        return [i, self.nodes[i].value, self.nodes[i].parent]
    def truthTable(self):
        d = {}
        d1 = {}
        for i in self.atomics:
            d.update({i : []})
        for i in range(0, 2**len(self.atomics)):
            s = str(bin(i + 2**len(self.atomics)))[3:]
            a = {}
            for j in range(len(s)):
                a.update({self.atomics[j]: True if s[j]=='1' else False})
            d = self.nodes[0].truthValue(self.nodes, {}, a)[2]
            for key in d:
                if key not in d1:
                    d1.update({key : []})
                d1[key].append(d[key][0])
        return d1


t = TreeProp('((G=F)>(G=F))')

print(pd.DataFrame(t.truthTable()))

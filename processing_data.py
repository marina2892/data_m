import pymongo
import networkx as nx
from networkx.algorithms.connectivity.disjoint_paths import edge_disjoint_paths
from networkx.algorithms.shortest_paths.generic import has_path

class Tasks:
    def __init__(self, user1, user2):
        self.start_users = (user1, user2)
        self.client = pymongo.MongoClient()
        self.db = self.client['instagram']


    def check_start_rel(self):
        if self.db[self.start_users[0]].estimated_document_count() == 0 or self.db[self.start_users[1]].estimated_document_count() == 0:
            return 0
        elif self.db[self.start_users[0]].find_one({'subscription': (self.start_users[1])}) and self.db[self.start_users[1]].find_one({'subscription': (self.start_users[0])}):
            return 1
        else:
            self.user_tree = nx.DiGraph()
            self.user_tree.add_nodes_from(self.start_users)
            self.list_nodes = list(self.user_tree.nodes).copy()
            return self.to_spider_iter(self.list_nodes)




    def to_spider_iter(self, list_nodes):
        for node in list_nodes:
            self.current_node = node
            if self.db[self.current_node].estimated_document_count() == 0:
                continue
            else:
                fl = 0
                for user in self.db[self.current_node].find({}, {'subscription': 1}):
                    for pred_node in self.user_tree.predecessors(self.current_node):
                        if user['subscription'] == pred_node:
                            fl = 1
                            break
                    if fl == 1:
                        continue
                    if user['subscription'] in list(self.user_tree.nodes):
                        continue
                    self.potential_node = user['subscription']
                    yield self.potential_node
        yield 0


    def check_rel(self):
       if self.db[self.potential_node].find_one({'subscription': (self.current_node)}):
            self.user_tree.add_node(self.potential_node)
            self.list_nodes.append(self.potential_node)
            self.user_tree.add_edge(self.current_node, self.potential_node)
            result = self.check_rel_to_opposite_base_node(self.potential_node)

            if not (isinstance(result, int)):
                return result
            else:
                return 0
       else:
           return 0


    def check_rel_to_opposite_base_node(self, user):
        if has_path(self.user_tree,self.start_users[0], user):
            base_node = self.start_users[0]
            opposite_base_node = self.start_users[1]
        else:
            base_node = self.start_users[1]
            opposite_base_node = self.start_users[0]
        if self.db[opposite_base_node].find_one({'subscription': user}) and self.db[user].find_one(
                {'subscription': opposite_base_node}):
            base_path = [t for t in edge_disjoint_paths(self.user_tree, base_node, user)][0]
            base_path.append(opposite_base_node)
            return base_path
        else:
            list_successors = [opposite_base_node]
            while 1:
                res = self.opposite_base_node_successors(user, list_successors)
                if (isinstance(res, str)):
                    base_path = [t for t in edge_disjoint_paths(self.user_tree, base_node, user)][0]
                    base_opposite_path = [t for t in edge_disjoint_paths(self.user_tree, opposite_base_node, res)][0]
                    base_opposite_path.reverse()
                    base_path.extend(base_opposite_path)
                    return base_path
                elif res == []:
                    break
                else:
                    list_successors = res
            return 0

    def opposite_base_node_successors(self,user, list_successors):
        for s in list_successors:
            l = []
            for node in self.user_tree.successors(s):
                if self.db[node].find_one({'subscription': user}) and self.db[user].find_one(
                        {'subscription': node}):
                    return node
                l.append(node)
            return l











#t = Tasks('_agentgirl_', 'reginatodorenko')
# a = t.check_potential_rel()
# i = 0
# for f in a:
#     print(f)
#     i = i+1
# print(i)
#a = t.check_start_rel()










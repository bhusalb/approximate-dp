import igraph as ig
# matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def build_graph(path):
    vars = dict()

    for condition in path['conditions']:
        vars[condition[1][1]] = path['variables'][condition[1][1]]
        vars[condition[3][1]] = path['variables'][condition[3][1]]

    keys_vars = list(vars.keys())
    length_of_vars = len(vars)
    g = ig.Graph(length_of_vars, directed=True)
    dict_var_index = dict()
    for i in range(length_of_vars):
        g.vs[i]['name'] = keys_vars[i]
        g.vs[i]['var'] = vars[keys_vars[i]]
        dict_var_index[keys_vars[i]] = i

    for condition in path['conditions']:
        if condition[2] == '<' or condition[2] == '<=':
            g.add_edge(
                dict_var_index[condition[1][1]],
                dict_var_index[condition[3][1]],
                **{
                    condition[1][1]: (condition[1][1], '<', condition[3][1]),
                    condition[3][1]: (condition[3][1], '>', condition[1][1]),
                },

            )
        else:
            g.add_edge(
                dict_var_index[condition[3][1]],
                dict_var_index[condition[1][1]],
                **{
                    condition[3][1]: (condition[3][1], '<', condition[1][1]),
                    condition[1][1]: (condition[1][1], '>', condition[3][1]),
                },
            )

    return g


def plot(g):
    fig, ax = plt.subplots(figsize=(5, 5))
    ig.plot(
        g,
        target=ax,
        layout="circle",  # print nodes in a circular layout
        vertex_size=30,
        vertex_frame_width=4.0,
        vertex_frame_color="white",
        vertex_label=g.vs["name"],
        vertex_label_size=7.0
    )

    plt.show()

"""
Network view support for inferelator CSV output
"""

def try_float(x):
    try:
        return float(x)
    except:
        return x

class InferelatorCSV:

    def __init__(self):
        self.line_dicts = []

    def read_csv(self, filename):
        f = open(filename)
        header_line = f.readline()
        headers = header_line.strip().split()
        self.headers = headers
        L = self.line_dicts
        while 1:
            line = f.readline().strip()
            if not line:
                break
            data = [try_float(x) for x in line.split()]
            d = dict(zip(headers, data))
            L.append(d)
        self.line_dicts = L

    def collections(self):
        headers = self.headers
        Dstats = {h: {} for h in headers}
        for d in L:
            for h in headers:
                dh = d[h]
                Dstats[h][dh] = Dstats[h].get(dh, 0) + 1
        self.Dstats = Dstats
        return Dstats

    def get_edges(self, source="regulator", dest="target"):
        edge_map = {}
        L = self.line_dicts
        for d in L:
            src = d[source]
            dst = d[dest]
            edge_map[(src, dst)] = d
        self.edge_map = edge_map
        return edge_map

    def related_edges(self, nodes, level=1):
        all_edges = self.get_edges()
        nodes = set(nodes)
        selected_edges = {}
        for iteration in range(level):
            related_nodes = set(nodes)
            for e in all_edges:
                (src, dst) = e
                if (src in nodes or dst in nodes) and e not in selected_edges:
                    related_nodes.add(src)
                    related_nodes.add(dst)
                    selected_edges[e] = all_edges[e]
            nodes = set(related_nodes)
        return selected_edges

    def related_subnetwork(self, nodes, level=1, html_file=None, weight="beta.sign.sum",
            **network_settings):
        """display related network as a widget (default) or HTML file."""
        edges = self.related_edges(nodes, level)
        if html_file:
            return network_html(html_file, edges, weight, **network_settings)
        else:
            # default: Jupyter network widget.
            return network_widget(edges, weight, **network_settings)

def network_widget(edge_map, weight="beta.sign.sum", **network_settings):
    from jp_doodle import directed_network
    settings = dict(
        title="Regulatory Network",
        default_layout="circle",
        separator_radius=6,
        link_radius=1,
        min_change=1,
        undo_limit=10,
        font="normal 10px Arial",  # default node font
        color="#fff", # default node color
        background="#259",  # default node background
        src_font=None,  # override src font
        src_color=None, # override src color
        src_background=None, # override src background
    )
    settings.update(network_settings)
    widget = directed_network.graph(**settings)
    for e in edge_map:
        d = edge_map[e]
        (src, dst) = e
        wt = d[weight]
        widget.edge(src, dst, wt)
    print ("network " + repr(widget) + " with", len(edge_map), "edges")
    widget.display_all()
    return widget

def network_html(html_file_name, edge_map, weight="beta.sign.sum", **network_settings):
    import json
    settings = dict(
        title="Regulatory Network",
        default_layout="circle",
        separator_radius=6,
        link_radius=1,
        min_change=1,
        undo_limit=10,
        font="normal 10px Arial",  # default node font
        color="#fff", # default node color
        background="#259",  # default node background
        src_font=None,  # override src font
        src_color=None, # override src color
        src_background=None, # override src background
    )
    settings.update(network_settings)
    edges = []
    for e in edge_map:
        (src, dst) = e
        d = edge_map[e]
        wt = d[weight]
        D = dict(src=src, dest=dst, wt=wt)
        edges.append(D)
    network_json = dict(edges=edges)
    settings["network_json"] = network_json
    json_str = json.dumps(settings, indent=1)
    subs = dict(JSON= json_str, title= settings["title"])
    html_txt = HTML_TEMPLATE % subs
    f = open(html_file_name, "w")
    f.write(html_txt)
    f.close()
    print ("wrote", len(html_txt), "to", html_file_name)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>

<title> %(title)s </title>


    <link rel="stylesheet" href="https://aaronwatters.github.io/jp_doodle/jquery-ui-1.12.1/jquery-ui.css">
    <script src="https://aaronwatters.github.io/jp_doodle/jquery-ui-1.12.1/external/jquery/jquery.js"></script>
    <script src="https://aaronwatters.github.io/jp_doodle/jquery-ui-1.12.1/jquery-ui.js"></script>

    <script src="https://aaronwatters.github.io/jp_doodle/jp_doodle_js/canvas_2d_widget_helper.js"></script>
    <script src="https://aaronwatters.github.io/jp_doodle/jp_doodle_js/dual_canvas_helper.js"></script>
    <script src="https://aaronwatters.github.io/jp_doodle/jp_doodle_js/nd_frame.js"></script>
    <script src="https://aaronwatters.github.io/jp_doodle/jp_doodle_js/gd_graph.js"></script>
    <script src="https://aaronwatters.github.io/jp_doodle/jp_doodle_js/directed_network.js"></script>
    <link rel=stylesheet href="https://aaronwatters.github.io/static/style.css">

</head>
<body>
        
<div id="target_container">
    <div id="target_div"/>
</div>
<script>
    var element = $('#target_div');

    function make_network_visualization(json_spec) {
        var N = element.directed_network(json_spec);
        N.display_all();
    };

    var json_spec = %(JSON)s;

    make_network_visualization(json_spec);

</script>    
</body>
</html>
"""

def relatedness_view(
    csv_filename,
    nodes,
    source="regulator",
    dest="target",
    weight="beta.sign.sum",
    html_file=None,
    level=1,
    **network_settings
    ):
    data = InferelatorCSV()
    data.read_csv(csv_filename)
    data.get_edges(source, dest)
    #edge_map = data.related_edges(nodes, level)
    return data.related_subnetwork(nodes, level, html_file, weight)

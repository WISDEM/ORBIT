# Post-Processing Script


import matplotlib.pyplot as plt
import re




def plot_supply_chain(df):
    fig, ax = plt.subplots(3, 1, figsize=(14, 7), sharex=True)
    components = ['Chain', 'Rope', 'Anchor']
    vessels = {'Chain': 'Railcar', 'Rope': 'Railcar', 'Anchor': 'Vessel'}

    df = df.copy()
    df['duration'] = df['duration'] / 24
    df['time'] = df['time'] / 24

    prod_pattern = lambda comp: re.compile(rf"^{comp}s? Production (\d+)$")

    for c, component in enumerate(components):
        vessel = vessels[component]
        leftlist = []

        # --- Dynamically find all production lines for this component ---
        prod_nums = set()
        for agent in df['agent']:
            match = prod_pattern(component).match(agent)
            if match:
                prod_nums.add(match.group(1))
        prod_nums = sorted(prod_nums, key=int)

        # --- Build ylabels for this component ---
        ylabels = []
        for num in prod_nums:
            ylabels.append(f'Manufacture {num}')
        ylabels += [
            'Transport Waiting',
            'Loading/Unloading',
            'Transport to Port/Manufacturer'
        ]
        for num in prod_nums:
            ylabels.append(f'Reset Machine {num}')
        ylabel_to_ynum = {label: i for i, label in enumerate(ylabels)}

        for _, row in df.iterrows():
            agent = row['agent']
            action = row['action']

            # Manufacture and Reset Machine (for each production line)
            prod_match = prod_pattern(component).match(agent)
            if prod_match and 'Manufacture' in action:
                prod_num = prod_match.group(1)
                ylabel = f'Manufacture {prod_num}'
                color = 'tab:blue'
            elif prod_match and 'Reset' in action:
                prod_num = prod_match.group(1)
                ylabel = f'Reset Machine {prod_num}'
                color = 'k'
            elif agent == f'{component} Transport {vessel}' and 'Waiting' in action:
                ylabel = 'Transport Waiting'
                color = 'tab:orange'
            elif agent == f'{component} Transport {vessel}' and 'Loading' in action:
                ylabel = 'Loading/Unloading'
                color = 'g'
            elif agent == f'{component} Transport {vessel}' and ('Full' in action or f'{component} arrives' in action or f'Transport {component}s' in action):
                ylabel = 'Transport to Port/Manufacturer'
                color = 'tab:green'
            elif agent == f'{component} Transport {vessel}' and 'Unload' in action:
                ylabel = 'Loading/Unloading'
                color = 'm'
            elif agent == f'{component} Transport {vessel}' and 'Empty' in action:
                ylabel = 'Transport to Port/Manufacturer'
                color = 'r'
            else:
                continue  # Skip unrelated rows

            ynum = ylabel_to_ynum[ylabel]
            width = row['duration']
            left = row['time'] - width
            leftlist.append(left)

            ax[c].barh(y=ynum, width=width, left=left, color=color, height=0.8)

        ax[c].set_yticks(range(len(ylabels)))
        ax[c].set_yticklabels(ylabels)
        ax[c].invert_yaxis()
        ax[c].set_title(f'{component}')

        if leftlist:
            nyears = int(max(leftlist) / 365)
            for i in range(nyears):
                ax[c].axvline(x=(i + 1) * 365, linestyle='dashed', linewidth=1.0, color='k')

    ax[-1].set_xlabel('Days')
    fig.suptitle('Supply Chain')
    fig.tight_layout()
    return fig, ax


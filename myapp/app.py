from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
import pandas as pd
import numpy as np
import random
from plotnine import ggplot, aes, geom_col, geom_line, geom_smooth, labs, geom_vline, geom_hline, scale_fill_discrete, annotate, coord_cartesian, theme_538, scale_fill_manual, geom_rect, theme, element_blank, scale_fill_grey

#%% parameters
demand_default = 60
n_renewables = 8
n_nuclear = 10
n_lignite = 22
n_hardcoal = 20
n_gas = 5
n_oil = 10
p_renewables = 5
p_nuclear = 10
p_lignite = 30
p_hardcoal = 32
p_gas = 70
p_oil = 120
p_renewables_eeg = 130

def createDf(n, p_low, p_high, name):
    df = pd.DataFrame({'source': [name] * n, 'price': np.random.randint(low=p_low, high=p_high, size=n), 'capacity': [1] * n})
    df.sort_values('price', inplace=True)
    return df
#%%
# df_renewables = createDf(n_renewables, p_low=p_renewables - 2, p_high=p_renewables + 2, name='Renewable')

#%%
df_nuclear = createDf(n_nuclear, p_low=p_nuclear - 0.1, p_high=p_nuclear + 0.1, name='Nuclear')
df_lignite = createDf(n_lignite, p_low=p_lignite - 10, p_high=p_lignite + 10, name='Lignite')
df_hardcoal = createDf(n_hardcoal, p_low=p_hardcoal - 10, p_high=p_hardcoal + 10, name='HardCoal')
df_gas = createDf(n_gas, p_low=p_gas - 20, p_high=p_gas + 20, name='Gas')
df_oil = createDf(n_oil, p_low=p_oil - 20, p_high=p_oil + 20, name='Oil')
df = pd.concat([df_nuclear, df_lignite, df_hardcoal, df_gas, df_oil])
df.sort_values('price', inplace=True)
df.reset_index(inplace=True)
df['number'] = df.index
df.drop(columns=['index'], axis=1, inplace=True)
        
#%%
app_ui = ui.page_fluid(
    ui.panel_title('Merit Order'),
    ui.p('How Prices are determined on Energy Markets'),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_slider("n_demand", "Demand", 60, 65, demand_default),
            ui.input_slider("n_renewables", "Add Renewables", 0, 25, 0),
        ui.input_slider("p_gas", "Gas Price", p_gas, 200, p_gas, step=10),
        ui.h4('Economic Impact'),
            ui.input_radio_buttons(
        "show_impact_renewables", "Show Economic Impact of Renewables?", {"yes": "Yes", "no": "No"}, selected='no'
    ),
            ui.input_radio_buttons(
        "is_gas_replaceable", "Is Gas replaceable?", {"yes": "Yes (well, in theory)", "no": "No (let's be realistic)"}
    ),
         ui.input_radio_buttons(
        "show_impact_high_gas_prices", "Show Economic Impact of High Gas Prices?", {"yes": "Yes", "no": "No"}, selected='no'
    ),
        ),
        ui.panel_main(
            ui.output_plot("plt_merit_order") 
        )
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    
    def df_filt():
        p_gas_new = input.p_gas()
        n_add = input.n_renewables()
        df_filt = df.copy()
        if p_gas_new != p_gas:
            df_filt.loc[df_filt['source']=='Gas', 'price'] = np.random.randint(low=-5, high=5, size=n_gas) + p_gas_new
            df_filt.sort_values('price', inplace=True)
            df_filt.reset_index(inplace=True)
            df_filt['number'] = df_filt.index
            df_filt.drop(columns=['index'], axis=1, inplace=True)
            
        if n_add > 0:
            df_renewables_add = createDf(n=n_add, p_low=p_renewables-2, p_high=p_renewables+2, name='Renewable')
            df_filt = pd.concat([df_filt, df_renewables_add])
            df_filt.sort_values('price', inplace=True)
            df_filt.reset_index(inplace=True)
            df_filt['number'] = df_filt.index
            
        if input.is_gas_replaceable() == 'no':
            nrows_df = len(df)
            nrows_filt = len(df_filt)
            df_gas = df_filt[df_filt['source']=='Gas'].copy()
            df_without_gas = df_filt[df_filt['source'] != 'Gas'].copy()
            nrows_gas = len(df_gas)
            nrows_wo_gas = len(df_without_gas.head(input.n_demand() - nrows_gas))
            # %% replace numbering based on Gas being not replaceable
            # 1.build df with max n_demand rows
            df_filt = pd.concat([df_without_gas.head(input.n_demand() - nrows_gas), df_gas])
            print(f"df: {nrows_df}, filt: {nrows_filt}, wo_gas: {nrows_wo_gas}")
            df_filt = pd.concat([df_filt, df_without_gas.tail(nrows_filt - nrows_wo_gas)])
            
            df_filt.reset_index(inplace=True)
            df_filt['number'] = df_filt.index

        
            
        return df_filt
        
    def market_price_default():
        return df.loc[df['number'] == input.n_demand(), 'price'].values[0]

    
    @output
    @render.plot
    def plt_merit_order():
        demand = input.n_demand()

        market_price = df_filt().loc[df_filt()['number'] == demand, 'price'].values[0]
        g = (ggplot(data= df_filt()) + 
            aes(x='number', y='price') + 
            geom_col(mapping=aes(fill='source')) + 
            # geom_smooth(span=0.4) + 
            labs(x = 'Supply Capacity [GW]', y='Marginal Costs [EUR/MWh]', title='Merit Order Energy Pricing') + 
            geom_vline(xintercept=demand, linetype='dotted', size = 1) +
            geom_hline(yintercept=market_price_default(), linetype='dotted', size = 1) + 
            scale_fill_discrete(name='Energy Source') +
            annotate('text', x=15, y=market_price_default() + 5, label = 'P Market (Default)') +
            annotate('text', x=demand_default-10, y=158, label = 'Demand') +
            coord_cartesian(ylim=[0, 200], xlim=[0, 110]) +
            scale_fill_manual({'Gas': 'blue', 'HardCoal': 'black', 'Lignite': 'brown', 'Nuclear': 'orange', 'Oil': 'red'}) +
            theme_538()
            # theme(axis_text_y=element_blank())
            )
        if input.n_renewables() > 0:
            g = (g +
            annotate('text', x=15, y=market_price + 5, label = 'P Market new', color='green') +
            geom_hline(yintercept=market_price, linetype='dotted', size = 1, color='grey')  +
            scale_fill_manual({'Gas': 'blue', 'HardCoal': 'black', 'Lignite': 'brown', 'Nuclear': 'orange', 'Oil': 'red', 'Renewable': 'green'})
            )
            if input.show_impact_renewables() == 'yes':
                g = (g + geom_rect(mapping=aes(xmin=0, xmax=input.n_renewables(), ymin=market_price_default(), ymax=p_renewables_eeg), fill='red', alpha=0.01) + 
                geom_hline(yintercept=p_renewables_eeg, linetype='dotted', size = 1, color='orange')  +
                annotate('text', x=15, y=p_renewables_eeg + 5, label = 'P EEG', color='orange') +
                geom_rect(mapping=aes(xmin=demand_default, xmax=demand_default+input.n_renewables(), ymin=market_price, ymax=market_price_default()), fill='green', alpha=0.01) + 
                scale_fill_grey()
                )
        if input.show_impact_high_gas_prices() == 'yes':
            x_range =df_filt().loc[df_filt()['source']=='Gas', 'number']
            xmin, xmax = x_range.min(), x_range.max()+1
            df_filt().to_csv('df.csv')
            p_market_new = df_filt().loc[df_filt()['source'] == 'Gas', 'price'].values.max()
            g = (g + geom_rect(mapping=aes(xmin=xmin, xmax=xmax, ymin=market_price_default(), ymax=p_market_new), fill='orange', alpha=0.01) + 
            geom_hline(yintercept=p_market_new, linetype='dotted', size = 1, color='orange')  +
            annotate('text', x=15, y=p_market_new + 5, label = 'P Market New', color='orange') +
            geom_rect(mapping=aes(xmin=0, xmax=demand_default-n_gas, ymin=market_price_default(), ymax=p_market_new), fill='red', alpha=0.01) + 
            scale_fill_grey()
            )
        return g 


app = App(app_ui, server)

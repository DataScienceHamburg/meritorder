#%% packages
import pandas as pd
import numpy as np

from plotnine import ggplot, aes, geom_col, geom_line, geom_smooth, labs, geom_vline, geom_hline, scale_fill_discrete, annotate, coord_cartesian, scale_color_manual, geom_point

# %%
n_renewables = 10
n_nuclear = 10
n_lignite = 20
n_hardcoal = 20
n_gas = 20
n_oil = 10
p_renewables = 5
p_nuclear = 10
p_lignite = 40
p_hardcoal = 60
p_gas = 100
p_oil = 140

def createDf(n, p_low, p_high, name):
    df = pd.DataFrame({'source': [name] * n_renewables, 'price': np.random.randint(low=p_low, high=p_high, size=n_renewables), 'capacity': [1] * n_renewables})
    df.sort_values('price', inplace=True)
    return df
#%%
df_renewables = createDf(n_renewables, p_low=p_renewables - 2, p_high=p_renewables + 2, name='Renewable')
df_nuclear = createDf(n_nuclear, p_low=p_nuclear - 0.1, p_high=p_nuclear + 0.1, name='Nuclear')
df_lignite = createDf(n_lignite, p_low=p_lignite - 10, p_high=p_lignite + 10, name='Lignite')
df_hardcoal = createDf(n_hardcoal, p_low=p_hardcoal - 10, p_high=p_hardcoal + 10, name='HardCoal')
df_gas = createDf(n_gas, p_low=p_gas - 20, p_high=p_gas + 20, name='Gas')
df_oil = createDf(n_oil, p_low=p_oil - 20, p_high=p_oil + 20, name='Oil')
df = pd.concat([df_renewables, df_nuclear, df_lignite, df_hardcoal, df_gas, df_oil])
df.sort_values('price', inplace=True)
df.reset_index(inplace=True)
df['number'] = df.index

#%%
demand = 55
market_price = df.loc[df['number'] == demand, 'price'].values[0]

#%%
(ggplot(data= df) +  
 aes(x='number', y='price') + 
 geom_col(mapping=aes(fill='source')) + 
 geom_smooth(span=0.4) + 
 labs(x = 'Supply Capacity [GW]', y='Marginal Costs [EUR/MWh]') + 
 geom_vline(xintercept=demand, linetype='dotted', size = 2) +
 geom_hline(yintercept=market_price, linetype='dotted', size = 2) + 
 scale_fill_discrete(name='Energy Source') +
 annotate('text', x=0, y=market_price + 5, label = 'P') +
 coord_cartesian(ylim=[0, 200], xlim=[0, 70])
 )

#%%

# %%
m = pd.DataFrame({'x':range(15), 'y':range(15), 'c': ['A']*5+['B']*5+['C']*5})
print(m)

# Plot x and y with colors mapped from 
#%% a dict
ggplot(m, aes('x','y', color='c')) + geom_point(size=3) + scale_color_manual({'A':'red', 'B':'violet', 'C': 'blue'})
# %%
df = pd.read_csv('df.csv', index_col=None)
n_demand = 65
df.drop(columns=['Unnamed: 0', 'index'], inplace=True)
df
# %%
df_gas = df[df['source']=='Gas'].copy()
df_without_gas = df[df['source'] != 'Gas'].copy()
nrows_wo_gas = len(df_without_gas)
nrows_gas = len(df_gas)
# %% replace numbering based on Gas being not replaceable
# 1.build df with max n_demand rows
df_new = pd.concat([df_gas, df_without_gas.head(n_demand - nrows_gas), df_without_gas.tail(nrows_gas)])
df_new.reset_index(inplace=True)
df_new['number'] = df_new.index
df_new  
# %%

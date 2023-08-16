import matplotlib.pyplot as plt
from plotnine import ggplot, aes, facet_grid, labs, geom_point, geom_line, theme, element_blank
import pandas as pd

def plot_indices(indices_df,plot_title_enp, plot_title_measure):
    "Lok Sabha Seat Share: Effective Number of Parties 1977-2019"

    #plt.style.use(['dark_background', 'ggplot'])
    #plt.title('HHI for India LS 1977-2019')
    #plt.xlabel('LS Year')
    #plt.ylabel('Herfindahl-Hirschman Index')
    #plt.scatter(ls_years, hhi)
    #plt.show()
    
    #plt.style.use(['dark_background', 'ggplot'])
    #plt.style.use('fivethirtyeight')
    
    #plt.xlabel('Lok Sabha Election Year')
    #plt.ylabel('Effective Number of Parties')
    #plt.scatter(ls_years, enp)
    #plt.title('Effective Number of Parties for LS 1977-2019')
    
    #plt.show()
    
    g1 = ggplot(indices_df, aes(x='year', y='enp')) + \
        labs(title=plot_title_enp) + \
        geom_line() + \
        geom_point(colour = "red", size = 3,alpha=0.4)
    
    indices_melt = indices_df.melt(id_vars=['year'], value_vars=['hhi','simpson',"shannon"], var_name='legend', value_name='a_or_b')

    g2 = ggplot(indices_melt, aes(x='year', y='a_or_b')) + geom_point(size=3,alpha=0.05) + \
        geom_line(aes(color='legend')) + \
        labs(y="", x="Election Year",title=plot_title_measure) + theme(legend_title=element_blank())
    
    return [g1,g2]

def plot_duo(india_df, us_df, plot_title_enp, measure='enp'):
    "Lok Sabha Seat Share: Effective Number of Parties 1977-2019"

    #plt.style.use(['dark_background', 'ggplot'])
    #plt.title('HHI for India LS 1977-2019')
    #plt.xlabel('LS Year')
    #plt.ylabel('Herfindahl-Hirschman Index')
    #plt.scatter(ls_years, hhi)
    #plt.show()
    
    #plt.style.use(['dark_background', 'ggplot'])
    #plt.style.use('fivethirtyeight')
    
    #plt.xlabel('Lok Sabha Election Year')
    #plt.ylabel('Effective Number of Parties')
    #plt.scatter(ls_years, enp)
    #plt.title('Effective Number of Parties for LS 1977-2019')
    
    #plt.show()
    india_df['country'] = 'india'
    us_df['country'] = 'us'
    melt_df = pd.concat([india_df[['country','year', measure]],    us_df[['country','year',measure]]])
    g1 = ggplot(melt_df, aes(x="year",y=measure, color='country')) + \
        labs(title=plot_title_enp) + geom_line() + geom_point()

    return g1


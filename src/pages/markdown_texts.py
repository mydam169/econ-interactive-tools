def intro_md():
    txt = '''
        ## Supply, demand and equilibrium

        On this page you will find several interactive tools designed to help you
        understand the basic demand and supply model. In particular, we will be looking at how
        equilibrium outcomes change as we modify the parameters of the supply and demand
        curve. We will also examine several implications on the market size, price and 
        welfare when the government intervenes by taxation or price fixing.

        In all cases, we consider the linear demand and supply model:
        $$
        \\begin{aligned}
        \\textbf{Demand:   } &P = a + bQ, \\\\
        \\textbf{Supply:   } &P = c + dQ,
        \\end{aligned}
        $$
        where $a>0$, $b<0$, $c>0$, $d>0$ and $a>c$. These are the parameters that can be modified
        using the sliders. 
        Observe that increasing $a$ is equivalent to
        increasing demand while increasing $c$ is reducing supply.

'''
    return txt

def home_md():
    txt = '''
        ## Welcome !
        ---
        On this website you will find several interactive tools.
        I've developed them in the hope of providing my students with visual aids
        of a number of basic economic concepts. 
        For ease of navigation, the site will be organized in chapters. 

        * Chapter 1: Basic supply and demand model
        * Chapter 2: Consequences of taxation
        * Chapter 3: Consequences of price fixing

'''
    return txt
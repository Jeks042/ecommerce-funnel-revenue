"""Render the milestone-three figures from the reproducible analysis summary."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
from analyse_funnel import blueprint

ROOT=Path(__file__).resolve().parents[1]


def render():
    summary=json.loads((ROOT/'reports/evidence/funnel-analysis-20261110.json').read_text())
    points=blueprint(summary)
    out=ROOT/'reports/figures';out.mkdir(exist_ok=True)
    sns.set_theme(style='whitegrid',font='DejaVu Sans',rc={'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False})
    plt.rcParams['svg.hashsalt']='ecommerce-funnel-v1'
    navy,teal,grey='#16384a','#087f8c','#526773'
    files=[]
    def save(fig,name):
        for ext in ['png','svg']:
            path=out/(name+'.'+ext)
            fig.savefig(path,dpi=180,facecolor='white',metadata={'Date':None} if ext=='svg' else {})
            if ext=='svg':
                # Canonical text survives Git's cross-platform line-ending normalisation.
                path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
            files.append(path)
        plt.close(fig)
    fig,ax=plt.subplots(figsize=(11.6,6.1))
    fig.subplots_adjust(left=.21,right=.70,top=.72,bottom=.20)
    fig.text(.045,.94,'The largest recorded gap is before the cart',fontsize=20,color=navy,weight='bold')
    fig.text(.045,.88,'December 2020 · 27,289 product-view visits within 131,418 eligible visits',fontsize=11,color=grey)
    labels=['Product view','Then cart','Then checkout','Then qualified purchase']
    values=points['journey_counts']
    ax.barh(range(4),values,color=[navy,teal,teal,teal],height=.57)
    ax.set_yticks(range(4),labels,fontsize=11);ax.invert_yaxis()
    ax.set_xlim(0,31000);ax.set_xticks([0,10000,20000,30000],['0','10,000','20,000','30,000'])
    ax.set_xlabel('Visits reaching each step in strict timestamp order',labelpad=12,fontsize=10)
    ax.grid(axis='y',visible=False)
    for i,v in enumerate(values):ax.text(v+350,i,f'{v:,}',va='center',fontsize=11,weight='bold',color=navy)
    ax.text(1.08,1.07,'Progression from prior step',transform=ax.transAxes,fontsize=10,weight='bold',color=navy)
    for i in range(1,4):
        ax.text(1.08,1-(i+.5)/4,f'{values[i]/values[i-1]:.1%}\n{values[i]:,} / {values[i-1]:,}',transform=ax.transAxes,va='center',fontsize=10,color=navy)
    fig.text(.045,.085,'Recorded progression is 5.27% from view to qualified purchase (1,437 / 27,289).',fontsize=10,color=navy)
    fig.text(.045,.038,'Source: reviewed GA4 sample aggregates, contract v1. 92 visits contain unresolved purchases.\nMissing next-step records do not prove abandonment, lost sales or a cause.',fontsize=9,color=grey)
    save(fig,'recorded_journey')

    fig,ax=plt.subplots(figsize=(11.6,7.0))
    fig.subplots_adjust(left=.22,right=.65,top=.73,bottom=.29)
    fig.text(.045,.95,'Mobile shows no broad progression disadvantage',fontsize=19,color=navy,weight='bold')
    fig.text(.045,.897,'Recorded device differences · December 2020 · all 31 dates retained',fontsize=11,color=grey)
    names=['View → cart','Cart → checkout','Checkout → purchase','View → purchase']
    comparisons=list(points['device_comparisons'].values())
    for i,c in enumerate(comparisons):
        lo,hi=c['leave_one_day_out_gap_pp']
        ax.plot([lo,hi],[i,i],color=teal,linewidth=3,alpha=.5)
        ax.scatter(c['standardized_gap_pp'],i,s=65,color=teal,zorder=4)
        ax.scatter(c['crude_gap_pp'],i-.13,s=48,marker='x',color=navy,zorder=4)
        ax.text(1.115,i,f"{c['all_counts'][0]['successes']:,} / {c['all_counts'][0]['denominator']:,}     {c['all_counts'][1]['successes']:,} / {c['all_counts'][1]['denominator']:,}",fontsize=10,color=navy,va='center',transform=ax.get_yaxis_transform())
    fig.text(.70,.77,'Observed successes / step visits',fontsize=10,color=navy,weight='bold')
    fig.text(.70,.739,'Desktop                 Mobile',fontsize=10,color=grey)
    ax.axvline(0,color=grey,linewidth=1,linestyle='--')
    ax.set_xlim(-2.2,2.2);ax.set_ylim(3.45,-.45)
    ax.set_yticks(range(4),names,fontsize=11);ax.grid(axis='y',visible=False)
    ax.set_xlabel('Mobile minus desktop (percentage points)\nPositive = higher recorded progression on mobile',fontsize=10,labelpad=10)
    legend=[Line2D([0],[0],marker='x',linestyle='',color=navy,label='Observed gap'),
        Line2D([0],[0],marker='o',linestyle='',color=teal,label='Same daily mix'),
        Line2D([0],[0],linewidth=3,alpha=.5,color=teal,label='Leave-one-date-out range')]
    fig.legend(handles=legend,loc='lower left',bbox_to_anchor=(.04,.10),ncol=3,frameon=False,fontsize=9)
    fig.text(.045,.065,'Ranges are date sensitivities, not confidence intervals. Each step uses its own daily denominator weights.',fontsize=9,color=grey)
    fig.text(.045,.025,'Source: reviewed GA4 sample aggregates, contract v1. Qualified recorded purchases; no causal or sales claim.\nTablet: 556 views, 164 carts, 62 checkouts, 30 completions; small later-step bases, counts only.',fontsize=9,color=grey)
    save(fig,'device_progression')
    receipt={'plot_data':points,'files_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'src/plot_funnel.py',ROOT/'src/analyse_funnel.py',ROOT/'reports/evidence/funnel-analysis-20261110.json']},
        'dependencies':{'matplotlib':matplotlib.__version__,'seaborn':sns.__version__},'visual_review':'Inspect PNGs at reading size before publication.'}
    (ROOT/'reports/evidence/funnel-figures-20261110.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Rendered two figures in PNG and SVG; recorded chart data and hashes.')


if __name__=='__main__':render()

"""Regenerate all four report figures into an isolated review directory."""
import argparse
from datetime import date,timedelta
import hashlib
import json
from pathlib import Path
import platform
import shutil
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import seaborn as sns
from report_data import ROOT,build
sys.path.insert(0,str(ROOT/'src'))
import plot_funnel

NAVY,TEAL,GREY,RED='#16384a','#087f8c','#526773','#b65242'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def render(output):
    output=Path(output).resolve()
    if not output.is_relative_to((ROOT/'private').resolve()):
        raise ValueError('Render into an isolated private/ review directory, then publish reviewed assets')
    figures=output/'figures';figures.mkdir(parents=True,exist_ok=True)
    # Reuse the accepted renderer without changing its pinned source or published assets.
    scratch=output/'legacy';(scratch/'src').mkdir(parents=True,exist_ok=True)
    (scratch/'reports/evidence').mkdir(parents=True,exist_ok=True)
    for name in ['src/plot_funnel.py','src/analyse_funnel.py','reports/evidence/funnel-analysis-20261110.json']:
        shutil.copyfile(ROOT/name,scratch/name)
    previous=plot_funnel.ROOT
    try:
        plot_funnel.ROOT=scratch;plot_funnel.render()
    finally:plot_funnel.ROOT=previous
    for path in (scratch/'reports/figures').iterdir():shutil.copyfile(path,figures/path.name)
    points=build()
    legacy_receipt=json.loads((scratch/'reports/evidence/funnel-figures-20261110.json').read_text(encoding='utf-8'))
    assert legacy_receipt['plot_data']==points['journey_and_devices'],'Legacy chart data changed'
    sns.set_theme(style='whitegrid',font='DejaVu Sans',rc={'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False})
    plt.rcParams['svg.hashsalt']='ecommerce-commercial-report-v1'
    def save(fig,name):
        for ext in ['png','svg']:
            p=figures/(name+'.'+ext)
            fig.savefig(p,dpi=180,facecolor='white',metadata={'Date':None} if ext=='svg' else {})
            if ext=='svg':p.write_text('\n'.join(x.rstrip() for x in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8',newline='\n')
        plt.close(fig)
    coverage=points['coverage'];daily=coverage['daily'];dates=[date.fromisoformat(r['date']) for r in daily]
    fig,axes=plt.subplots(3,1,figsize=(11.6,7.0),sharex=True)
    fig.subplots_adjust(left=.14,right=.96,top=.78,bottom=.20,hspace=.35)
    fig.text(.045,.95,'Recording gaps shape the comparison period',fontsize=20,weight='bold',color=NAVY)
    fig.text(.045,.895,'18 November dates have no cart events, while checkout and purchase records continue.',fontsize=11,color=GREY)
    fig.text(.69,.825,'SHADED: DECEMBER ANALYSIS PERIOD',fontsize=9,color=TEAL,weight='bold')
    for ax,key,label in zip(axes,['cart_events','checkout_events','purchase_events'],['Cart events','Checkout events','Raw purchase\nevents']):
        ax.axvspan(date(2020,12,1),date(2021,1,1),color='#ddf0f0',zorder=0)
        ax.bar(dates,[r[key] for r in daily],width=.8,color=TEAL if key=='cart_events' else NAVY,zorder=2)
        ax.set_ylabel(label,fontsize=10,color=NAVY);ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
        ax.grid(axis='x',visible=False);ax.set_ylim(bottom=0)
    zeros=[date(int(d[:4]),int(d[4:6]),int(d[6:])) for d in coverage['zero_cart_dates']]
    axes[0].scatter(zeros,[0]*len(zeros),marker='|',s=90,color=RED,zorder=4,clip_on=False)
    ticks=[date(2020,11,1),date(2020,11,15),date(2020,12,1),date(2020,12,15),date(2021,1,1),date(2021,1,15),date(2021,1,31)]
    axes[-1].set_xticks(ticks,[d.strftime('%d %b') for d in ticks],fontsize=9)
    axes[-1].set_xlim(date(2020,10,31),date(2021,2,1))
    fig.text(.045,.10,'Red marks identify observed zero-cart dates. Separate vertical scales show event counts, not conversion rates.',fontsize=9,color=GREY)
    fig.text(.045,.045,'Source: 92-day GA4 sample event audit, 1 Nov 2020–31 Jan 2021; all devices, before visit eligibility.\nZero events do not establish why recording is absent. No missing dates are filled or treated as zero.',fontsize=9,color=GREY)
    save(fig,'recording_coverage')

    scenario=points['scenarios'];rows=scenario['rows']
    fig,ax=plt.subplots(figsize=(11.6,6.7));fig.subplots_adjust(left=.36,right=.96,top=.72,bottom=.20)
    fig.text(.045,.95,'Cart growth does not establish purchase growth',fontsize=20,weight='bold',color=NAVY)
    fig.text(.045,.89,'HYPOTHETICAL · 27,289 product-view visits as the reference cohort size',fontsize=11,color='#946322',weight='bold')
    labels=[]
    for r in rows:
        delta=float(r['absolute_cart_rate_change'])*100
        unit='percentage point' if abs(delta)==1 else 'percentage points'
        name='No change' if delta==0 else f'{delta:+g} {unit}'
        labels.append(name+'\n'+r['additional_carts_display']+' additional cart visits')
    sns.heatmap([[float(v) for v in r['completion_values']] for r in rows],
        annot=[r['completion_display'] for r in rows],fmt='',cmap=sns.diverging_palette(15,190,as_cmap=True),
        center=0,vmin=-100,vmax=100,cbar=False,linewidths=2,linecolor='white',ax=ax,
        xticklabels=['No downstream\nprogression','Half the observed\ndownstream ratio','The observed\ndownstream ratio'],
        yticklabels=labels,annot_kws={'fontsize':13})
    ax.tick_params(axis='y',rotation=0,labelsize=10);ax.tick_params(axis='x',rotation=0,labelsize=10)
    ax.xaxis.tick_top();ax.set_xlabel('');ax.set_ylabel('')
    fig.text(.045,.12,'Cell values: additional visits completing the recorded sequence under each assumption.',fontsize=10,color=NAVY)
    fig.text(.045,.065,'Observed downstream reference: 1,437 completions / 7,874 carts. Existing behaviour is otherwise held fixed.\nFractions are arithmetic equivalents; no incremental sales, revenue or probability bounds are established.',fontsize=9,color=GREY)
    save(fig,'cart_scenarios')
    files=sorted(figures.glob('*'))
    manifest={'python_version':platform.python_version(),'dependencies':{'matplotlib':matplotlib.__version__,'seaborn':sns.__version__},
        'plot_data':points,'rendered_sha256':{p.name:sha(p) for p in files},
        'accepted_asset_byte_matches':{p.name:(sha(p)==sha(ROOT/'reports/figures'/p.name)) for p in files if (ROOT/'reports/figures'/p.name).exists()},
        'interpretation':'Rendered from accepted aggregates only. Numeric data must match; image bytes may differ across platforms.'}
    (output/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Regenerated four report figures as eight PNG/SVG files in the private review directory.')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'private/report-build');args=parser.parse_args()
    render(args.output)

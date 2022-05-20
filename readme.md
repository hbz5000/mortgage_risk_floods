_zenodo placeholder_

# thomson-etal_journal_tbd

**Systemic financial risk arising from residential flood loss**

Hope Thomson<sup>1\*</sup>, Antonia Sebastian<sup>2</sup>, Harrison Zeff<sup>3</sup>, Rachel Kleiman<sup>3</sup>,and Gregory W. Characklis<sup>3</sup>,

<sup>1 </sup> Environmental Finance Center, University of North Carolina at Chapel Hill
<sup>2 </sup> Department of Earth, Marine and Environmental Sciences, University of North Carolina at Chapel Hill
<sup>3 </sup> Center on Financial Risk in Environmental Systems, University of North Carolina at Chapel Hill


\* corresponding author:  zeff@live.unc.edu

## Abstract
Large flood events are known to be destructive, but we don’t understand exactly how that they impact our society. For one, a lot of people experience flood damage that is uninsured, but we aren’t able to count up these damage costs as easily as we are insured damage. Additionally, over time the flood can cause other impacts, such as decreases in property values. These effects together can make it difficult for property owners to recover from the flood. In some cases, damage and property value decrease can encourage abandonment of the property. This can create financial consequences for the property owner, the mortgage lender, or a government.
To see the size of these consequences, we modelled the uninsured damage, property value decreases, and mortgage payments over time in eastern North Carolina. We used data about properties, their finances, and the surrounding environment within specialized computer code to look at Hurricane Florence, a large storm that caused widespread flooding in the study area. In the results of the model, we see that uninsured damage and property value decreases outweigh the insured damage. We also see that property owners face the potential for large financial consequences, as do lenders and local governments. These consequences vary by regions and within communities, making it difficult to create thorough plans to prepare for future floods. Properties with lower values are especially likely to be abandoned and create delayed financial consequences after a flood, raising concerns about who is impacted by the flood long-term. These flood impacts can slow down post-flood recovery efforts and areas may still be recovering when another flood occurs. Planning efforts should account for these delayed impacts and the potential for additional financial consequences after a flood.
## Journal reference
Thomson. H., et al. (TBD). Systemic financial risk arising from residential flood loss (in preparation).

## Code reference: TMI
Zenodo link:
Human, I.M. (2021, April 14). Project/repo:v0.1.0 (Version v0.1.0). Zenodo. http://doi.org/some-doi-number/zenodo.7777777

## Data reference
Parcel Data: https://www.nconemap.gov/
Land Cover Data: https://www.mrlc.gov/
Hydrography Data: https://www.usgs.gov/national-hydrography/nhdplus-high-resolution
Soil Data: https://websoilsurvey.sc.egov.usda.gov/App/WebSoilSurvey.aspx
NFIP (public) Data: https://www.fema.gov/about/openfema/data-sets
Property Sales Data (private): https://www.attomdata.com/
Mortgage Data: https://ffiec.cfpb.gov/data-publication/dynamic-national-loan-level-dataset
Mortgage Perforamnce Data: https://capitalmarkets.fanniemae.com/credit-risk-transfer/single-family-credit-risk-transfer/fannie-mae-single-family-loan-performance-data

## Reproduce my experiment
Because of their reliance on private property transaction and FEMA policy/claim data, the three sub-models (ML flood damage, kriging property value, stochastic mortgage repayment) cannot be shared here. Anonymized parcel-level output from each model is included in the public_input_files folder.  Scripts to perform the agent-based decision tree analysis and create figures are included here

1. Download the scripts: decision_tree_public.py & make_underwater_mortgage_plots.py from mortgage_flood_risk repo
2. Download public_input_files folder from link at: https://drive.google.com/drive/folders/1jYi89ydN9GFGsxrbFB11OQ8IQifsvChT?usp=sharing
2. Place scripts and public_input_files folder in working directory, check that files: damage_output_public.csv, ltv_output_public.csv, and pv_output_public.csv; are in folder: public_input_files
3. Run decsision_tree_public.py to write output_abdt_public_(current_date).csv to working directory

## Reproduce my figures
4. Run make_underwater_mortgage_plots.py to create figures from Thomson et al. (2022) in working directory
5. Look at figures


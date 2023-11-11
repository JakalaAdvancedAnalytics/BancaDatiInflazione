
import streamlit as st
import pandas as pd 
from PIL import Image
import altair as alt 
import numpy as np

#leggo file di input 
input_file = pd.read_csv('Analisi_Import_dashboard.txt', sep = '|')


var_pct = ['inflazione_pct', 
            'over_reddito_new_mean',
            'over_reddito_post_mean',
            'riduzione_c_reali_max',
            'riduzione_c_reali_min',
            'gap_max_pct_vs_reddito']
dim_order = ['split_reddito', 'split_reddito_byreg', 'split_liquidita', 'split_liquidita_byreg','indice_inflazione_round']

###### RECODING DELLE SELEZIONI
#variabile di analisi 
def my_recode_analisi(selection):
    if selection == "Media indice inflazione":
        return 'inflazione_pct'
    elif selection == "Percentuale famiglie con consumi sopra reddito a causa dell'inflazione":
        return 'over_reddito_new_mean'
    elif selection == 'Percentuale famiglie con consumi sopra reddito':
        return 'over_reddito_new_mean' ### in questo caso faccio un bar chart con le famiglie che erano sopra reddito prima inflazione e quelle nuove
    #elif selection == 'Media € consumi sopra reddito':
        #return 'gap_max_mean'
    elif selection == 'Totale € consumi sopra reddito (milioni)':
        return 'gap_max_sum'
    elif selection == "% riduzione attesa dei consumi reali":
        return 'riduzione_c_reali_max'
    elif selection == 'Totale numero famiglie':
        return 'conta_sum'
    else:
        return ''
        
#variabile di dimensione
def my_recode_dimensione(selection):
    if selection == "Totale":
        return 'all_v'
    elif selection == 'Area geografica':
        return 'zona5'
    elif selection == "Genere capofamiglia":
        return 'genere'
    elif selection == 'Cittadinanza capofamiglia':
        return 'cittadinanza'
    elif selection == 'Titolo di studio capofamiglia':
        return 'titolo_studio'
    elif selection == 'Condizione professionale capofamiglia':
        return 'cond_prof'
    elif selection == 'Tipologia occupazionale capofamiglia':
        return 'lavoro5'
    elif selection == 'Tipologia famiglia':
        return 'tip_fam'
    elif selection == 'Decili di reddito':
        return 'split_reddito'
    elif selection == 'Decili di reddito per regione':
        return 'split_reddito_byreg'
    elif selection == 'Decili di liquidità':
        return 'split_liquidita'
    elif selection == 'Decili di liquidità per regione':
        return 'split_liquidita_byreg'
    elif selection == 'Livello di inflazione personale':
        return 'indice_inflazione_round'
    elif selection == 'Provincia':
        return 'nprov'    
    elif selection == 'Regione':
        return 'nreg'     
    else:
        return ''
        

#leggo data di aggiornamento istat 
aggiornamento_istat = input_file['aggiornamento_istat'].iloc[0] 


#preparo valori per filtri 
filtro_geo = list((set(input_file[input_file['var_territorio'].notnull()]['var_territorio'])))
dimensioni_analisi =  (set(input_file[input_file['var'].notnull()]['var']))


#########
# SIDEBAR 
image = Image.open('MicrosoftTeams-image.png')
st.sidebar.image(image, width=225)

st.sidebar.subheader("Imposta i criteri di analisi")
default_geo = filtro_geo.index('TOTALE ITALIA')
add_selectbox_geo = st.sidebar.selectbox("Seleziona l'area geografica da analizzare",
    (filtro_geo), index = default_geo)

add_selectbox_analisi = st.sidebar.selectbox('Seleziona la variabile di analisi',
    ('Media indice inflazione', 
    "Percentuale famiglie con consumi sopra reddito a causa dell'inflazione",
    'Percentuale famiglie con consumi sopra reddito', 
    'Totale € consumi sopra reddito (milioni)',
    #'% € consumi sopra reddito vs reddito',
    "% riduzione attesa dei consumi reali",
    'Totale numero famiglie'))

add_selectbox_dimensione = st.sidebar.selectbox('Seleziona la dimensione di analisi',
    ('Totale',
    'Area geografica',
    'Decili di reddito',
    'Decili di reddito per regione',
    'Decili di liquidità',
    'Decili di liquidità per regione',
    'Livello di inflazione personale',
    'Genere capofamiglia',
    'Cittadinanza capofamiglia',
    'Titolo di studio capofamiglia',
    'Condizione professionale capofamiglia',
    'Tipologia occupazionale capofamiglia',
    'Tipologia famiglia',
    'Provincia',
    'Regione'
    ))


st.sidebar.subheader(" ")
st.sidebar.subheader(" ")
st.sidebar.subheader(" ")
st.sidebar.subheader("Vuoi saperne di più?")
with open('DataLab_IndiceInflazione.pdf', 'rb') as f:
	st.sidebar.download_button('Scarica doc di approfondimento', f, file_name='DataLab_IndiceInflazione.pdf')  # Defaults to 'application/octet-stream'
st.sidebar.subheader("Oppure contattaci! info@jakala.com")

###### RECODING DELLE SELEZIONI
add_selectbox_analisi_var = my_recode_analisi(add_selectbox_analisi)
add_selectbox_dimensione_var = my_recode_dimensione(add_selectbox_dimensione)


#### TITOLO 
st.markdown("<h2 style='text-align: center; color: black;'>La banca dati Jakala per studiare l'impatto dell'inflazione</h2>", unsafe_allow_html=True)
st.markdown("<h6 style='text-align: center; color: black;'>Analisi descrittiva di sintesi - Aggiornamento dati ISTAT a: " + aggiornamento_istat + "</h6>", unsafe_allow_html=True)

st.text(" ")
st.text(" ")
st.text(" ")

########################
########################
### GRAFICO IN BASE ALLE SELEZIONI 

analisi = input_file[(input_file['var_territorio'] == add_selectbox_geo) & 
    (input_file['var'] == add_selectbox_dimensione_var)
    ][[add_selectbox_analisi_var, 'mod']]



analisi_long = analisi.melt(add_selectbox_analisi_var, value_name='modalita')


#se seleziono % famiglie sopra reddito, voglio fare stacked bar chart con % famiglie sopra reddito prima di inflazione e quelle che si sono aggiunte  
if add_selectbox_analisi == "Percentuale famiglie con consumi sopra reddito":
    analisi_over_reddito_pre = input_file[(input_file['var_territorio'] == add_selectbox_geo) & 
        (input_file['var'] == add_selectbox_dimensione_var)
        ][['over_reddito_pre_mean', 'mod']]  

    analisi_over_reddito_pre_long = analisi_over_reddito_pre.melt('over_reddito_pre_mean', value_name='modalita')
    analisi_over_reddito_pre_long['over_reddito_new_mean'] = analisi_over_reddito_pre_long['over_reddito_pre_mean'] #corretto --> mi serve per appendere il file a quello che analizza i nuovi passati sopra reddito 
    analisi_long['TIME'] = "A causa dell'Inflazione"
    analisi_over_reddito_pre_long['TIME'] = "Già prima dell'Inflazione"
    analisi_long = analisi_over_reddito_pre_long.append(analisi_long)


#se seleziono % riduzione consumi reali, voglio fare grouped bar chart, con riduzione min - max (intaccando liquidità oppure no)  
if add_selectbox_analisi == "% riduzione attesa dei consumi reali":
    analisi_riduzione_min = input_file[(input_file['var_territorio'] == add_selectbox_geo) & 
        (input_file['var'] == add_selectbox_dimensione_var)
        ][['riduzione_c_reali_min', 'mod']]  

    analisi_riduzione_min_long = analisi_riduzione_min.melt('riduzione_c_reali_min', value_name='modalita')
    analisi_riduzione_min_long['riduzione_c_reali_max'] = analisi_riduzione_min_long['riduzione_c_reali_min'] #corretto --> mi serve per appendere il file
    analisi_long['TIME'] = "Massimo -- senza intaccare risparmi"
    analisi_riduzione_min_long['TIME'] = "Minimo -- intaccando risparmi"
    analisi_long = analisi_riduzione_min_long.append(analisi_long)
    
                                                                                          
# Horizontal stacked bar chart
# asse x --> differenza per formato percentuale o no
if add_selectbox_analisi_var in var_pct:
    asse_x = alt.X(add_selectbox_analisi_var, 
                type="quantitative", 
                title=add_selectbox_analisi,
                axis=alt.Axis(format='%'),
                )
else:
    asse_x = alt.X(add_selectbox_analisi_var, 
                type="quantitative", 
                title=add_selectbox_analisi,
                )

# asse y --> differenza se tenere ordine logico (es.: decili di reddito), oppure ordinare in base al kpi decrescente
if add_selectbox_dimensione_var in dim_order:
    asse_y= alt.Y("modalita", 
                type = "nominal",  
                title=add_selectbox_dimensione,  
                )
else:
    asse_y = alt.Y("modalita", 
                type = "nominal",  
                title=add_selectbox_dimensione,  
                sort=alt.EncodingSortField(field=add_selectbox_analisi_var, op='mean', order='descending')
                )

# aggiunta --> se kpi = % famiglie sopra reddito, il grafico diventa uno stacked bar (famiglie che erano sopra reddito prima e quelle che si sono aggiunte)
if add_selectbox_analisi in ["Percentuale famiglie con consumi sopra reddito", "% riduzione attesa dei consumi reali"]:
    colore = alt.Color("TIME", type="nominal", title="", legend = alt.Legend(orient='bottom', columns = 1, rowPadding=2, ))
    ordine = alt.Order("TIME", sort="descending")
else:
    colore= alt.Color("variable", type="nominal", title="", legend = None)
    ordine = alt.Order("variable")

if add_selectbox_analisi != "% riduzione attesa dei consumi reali":
    chart = (
        alt.Chart(analisi_long)
        .mark_bar()
        .encode(
            x=asse_x,
            y=asse_y,
            color=colore,
            order=ordine,
        )
    )
else:
    chart = (
        alt.Chart(analisi_long)
        .mark_bar()
        .encode(
            x=asse_x,
            y=alt.Y('TIME:O', axis=alt.Axis(labels=False, title = " " )),
            row = asse_y , 
            color=colore,
            order=ordine,
        )
    )


if add_selectbox_dimensione == "Totale":
    st.markdown("<h6 style='text-align: center; color: black;'> " + add_selectbox_analisi + " per il totale dell'area selezionata</h6>", unsafe_allow_html=True)
else:
    st.markdown("<h6 style='text-align: center; color: black;'> " + add_selectbox_analisi + " splittato per " + add_selectbox_dimensione + "</h6>", unsafe_allow_html=True)

st.altair_chart(chart , use_container_width=True)


################################
################################
## se seleziono indice inflazione come kpi, e seleziono "totale" come dimensione di analisi faccio anche grafico della distribuzione delle famiglie 

if add_selectbox_analisi_var == 'inflazione_pct' and add_selectbox_dimensione == "Totale":
    analisi_inf = input_file[(input_file['var_territorio'] == add_selectbox_geo) & 
        (input_file['var'] == 'indice_inflazione_round')
        ][['conta_sum', 'mod']]

    analisi_inf_long = analisi_inf.melt('conta_sum', value_name='modalita')


    asse_x = alt.X("modalita", 
                type="nominal", 
                title="Valore indice inflazione",
                axis=alt.Axis(format=".0%"),
                )

    asse_y= alt.Y("conta_sum", 
                type = "quantitative",  
                title="Numero di famiglie",  
                )

    chart = (
        alt.Chart(analisi_inf_long)
        .mark_bar()
        .encode(
            x=asse_x,
            y=asse_y,
        )
    )

    st.text("")
    st.markdown("<h6 style='text-align: center; color: black;'>Distribuzione delle famiglie per valore dell'indice di inflazione</h6>", unsafe_allow_html=True)
    st.altair_chart(chart , use_container_width=True)





###################################################
###################################################
### mappa delle province 

#se selezione è famiglie sopra reddito, non ho più lo stacked bar chart 
#quindi considero il kpi che misura il totale famiglie con consumi > reddito dopo l'inflazione 
if add_selectbox_analisi == "Percentuale famiglie con consumi sopra reddito":
    add_selectbox_analisi_var = 'over_reddito_post_mean'


st.text(" ")
st.text(" ")
if add_selectbox_analisi_var != "riduzione_c_reali_max":
    titolo = "Mappa per provincia di: " + add_selectbox_analisi
else:
    titolo = "Mappa per provincia di: " + add_selectbox_analisi + " - massima - senza intaccare i risparmi"

st.markdown("<h6 style='text-align: center; color: black;'>" + titolo + "</h6>", unsafe_allow_html=True)


#scarico la geografia utilizzabile nei grafici di altair
province_mappa = alt.topo_feature("https://raw.githubusercontent.com/deldersveld/topojson/master/countries/italy/italy-provinces.json", 
    'ITA_adm2',
    )

#estraggo il dato per provincia
#devo sistemare il nome delle province per poter matchare con geografia 
#devo gestire anche puntualmente le province sarde 
province = input_file[(input_file['var'] == 'nprov') & (input_file['var_territorio'] == 'TOTALE ITALIA')]
province['NAME_2'] = province.apply(lambda row: row.nprov.capitalize(), axis = 1) 
province = province[['NAME_2', add_selectbox_analisi_var, 'riduzione_c_reali_min']]

nuoro = province[province['NAME_2'] == 'Nuoro']
nuoro['NAME_2'] = 'Ogliastra' 
olbia = province[province['NAME_2'] == 'Sassari']
olbia['NAME_2'] = 'Olbia-Tempio' 
campidano = province[province['NAME_2'] == 'Sud sardegna']
campidano['NAME_2'] = 'Medio Campidano' 
carbonia = province[province['NAME_2'] == 'Sud sardegna']
carbonia['NAME_2'] = 'Carbonia-Iglesias' 
province = province.append(nuoro).append(olbia).append(campidano).append(carbonia)

province['NAME_2'] = np.where(province['NAME_2'] == 'Verbano-cusio-ossola', 'Verbano-Cusio-Ossola', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Monza e della brianza', 'Monza and Brianza', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Mantova', 'Mantua', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Padova', 'Padua', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == "Reggio nell'emilia", "Reggio Nell'Emilia", province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'La spezia', 'La Spezia', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Firenze', 'Florence', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Forlì-cesena', "Forli' - Cesena", province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Pesaro e urbino', 'Pesaro E Urbino', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Ascoli piceno', 'Ascoli Piceno', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == "L'aquila", "L'Aquila", province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Barletta-andria-trani', 'Barletta-Andria-Trani', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Reggio di calabria', 'Reggio Di Calabria', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Siracusa', 'Syracuse', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Massa-carrara', 'Massa Carrara', province['NAME_2'])
province['NAME_2'] = np.where(province['NAME_2'] == 'Vibo valentia', 'Vibo Valentia', province['NAME_2'])



if add_selectbox_analisi_var in var_pct:
    colore_mappa = alt.Color(add_selectbox_analisi_var + ":Q", legend=alt.Legend(format=".0%", title=""))
else:
    colore_mappa = alt.Color(add_selectbox_analisi_var + ":Q", legend=alt.Legend(title="")) 

map = alt.Chart(province_mappa).mark_geoshape(stroke='white',strokeWidth=0.125).encode(
    color=colore_mappa,
).transform_lookup(
    lookup='properties.NAME_2',
    from_=alt.LookupData(province, 'NAME_2', [add_selectbox_analisi_var])
).properties(
    width=700,
    height=500
)

st.altair_chart(map, use_container_width=False)

#se scelgo "% riduzione consumi reali", faccio seconda mappa con l'ipotesi di riduzione minima
if add_selectbox_analisi_var == 'riduzione_c_reali_max':

    titolo = "Mappa per provincia di: " + "% riduzione attesa dei consumi reali" + " - minima - intaccando i risparmi"
    st.markdown("<h6 style='text-align: center; color: black;'>" + titolo + "</h6>", unsafe_allow_html=True)

    map = alt.Chart(province_mappa).mark_geoshape(stroke='white',strokeWidth=0.125).encode(
        color=alt.Color("riduzione_c_reali_min:Q", legend=alt.Legend(format=".0%", title="")),  #corretto, la mappa con riduzione in ipotesi massimo è quella che ho fatto sopra 
    ).transform_lookup(
        lookup='properties.NAME_2',
        from_=alt.LookupData(province, 'NAME_2', ["riduzione_c_reali_min"])
    ).properties(
        width=700,
        height=500
    )

    st.altair_chart(map, use_container_width=False)





#########################################
#########################################
### EXPANDER CON DESCRIZIONI

with st.expander("Dettagli"):
    st.markdown("<h6 style='text-align: center; color: black;'>Definizioni variabili di analisi</h6>", unsafe_allow_html=True)
    st.write("Media indice inflazione: inflazione per la categoria selezionata. Inflazione ottenuta come media degli ultimi 12 mesi disponibili") 
    st.write("Percentuale famiglie con consumi sopra reddito a causa dell'inflazione: quota di famiglie i cui consumi nominali, a causa dell'inflazione, diventano maggiori del reddito (ipotizzando stabilità di consumi reali)") 
    st.write("Percentuale famiglie con consumi sopra reddito: quota di famiglie i cui consumi risultano maggiori del reddito. Sono differenziate le famiglie in questa situazione già prima dell'impatto dell'inflazione da quelle ritrovatesi in questa situazione a causa dell'inflazione") 
    st.write("Totale € consumi sopra reddito (milioni): per le famiglie con consumi maggiori del reddito, valor totale (milioni €) del gap di consumi rispetto al reddito") 
    #st.write("% € consumi sopra reddito vs reddito: per le famiglie con consumi maggiori del reddito, percentuale del gap di consumi rispetto al reddito") 
    st.write("% riduzione attesa dei consumi reali: percentuale di riduzione attesa dei consumi reali nella doppia ipotesi (massima: le famiglie NON intaccano lo stock di risparmi -- minima: le famiglie ricorrono ai rispami liquidi)")
    st.write("Totale numero famiglie: numero di famiglie per la categoria") 
    st.write("")
    st.write("")
    st.markdown("<h6 style='text-align: center; color: black;'>Definizioni dimensioni di analisi</h6>", unsafe_allow_html=True)   
    st.write("Totale: totale delle famiglie per l'area geografica selezionata")
    st.write("Area geografica: suddivisione in 5 aree geografiche")
    st.write("Decili di reddito: suddivisione delle famiglie in base a decili di reddito (10 gruppi di uguali dimensioni dal reddito più basso al reddito più alto)")
    st.write("Decili di reddito per regione: suddivisione delle famiglie in base a decili di reddito calcolati all'interno di ogni regione (10 gruppi di uguali dimensioni dal reddito più basso al reddito più alto)")
    st.write("Decili di liquidità: suddivisione delle famiglie in base a decili di liquidità disponibile (10 gruppi di uguali dimensioni dal livello di liquidità più basso a quello più alto)")
    st.write("Decili di liquidità per regione: suddivisione delle famiglie in base a decili di liquidità disponibili calcolati all'interno di ogni regione (10 gruppi di uguali dimensioni dal livello di liquidità più basso a quello più alto")
    st.write("Livello di inflazione personale: classificazione delle famiglie in base al proprio livello di inflazione (derivato dalla provincia di residenza e dal proprio paniere di consumi)")
    st.write("Genere capofamiglia: genere del capofamiglia M/F")
    st.write("Cittadinanza capofamiglia: cittadinanza del capofamiglia Italiano/Straniero")
    st.write("Titolo di studio capofamiglia: titolo di studio del capofamiglia")
    st.write("Condizione professionale capofamiglia: condizione professionale del capofamiglia")
    st.write("Tipologia occupazionale capofamiglia: tipologia occupazionale del capofamiglia")
    st.write("Tipologia famiglia: tipologiadi famiglia")
    st.write("Provincia: provincia di residenza")
    st.write("Regione: regione di residenza")
      

import streamlit as st
import pandas as pd
import smartsheet
import streamlit.components.v1 as components

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time





@st.cache_data(ttl=300)
def smartsheet_to_dataframe(sheet_id):
    smartsheet_client = smartsheet.Smartsheet(st.secrets['smartsheet']['access_token'])
    sheet             = smartsheet_client.Sheets.get_sheet(sheet_id)
    columns           = [col.title for col in sheet.columns]
    rows              = []
    for row in sheet.rows: rows.append([cell.value for cell in row.cells])
    return pd.DataFrame(rows, columns=columns)





def submit_to_smartsheet(df):
    smartsheet_client = smartsheet.Smartsheet(st.secrets['smartsheet']['access_token'])
    sheet             = smartsheet_client.Sheets.get_sheet(st.secrets['smartsheet']['sheets']['submissions'])
    column_map        = {col.title: col.id for col in sheet.columns}
    rows              = []

    for _, row_data in df.iterrows():
        row = smartsheet.models.Row()
        row.to_top = True
        row.cells = [
            {"column_id": column_map[col], "value": row_data[col]}
            for col in df.columns
        ]
        rows.append(row)

    smartsheet_client.Sheets.add_rows(st.secrets['smartsheet']['sheets']['submissions'], rows)





@st.cache_data(ttl=300)
def loading_details(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(2)

        bedrooms    = driver.find_element(By.XPATH, "//*[@id='page-content']/div/main/div[2]/article/footer/div[1]/div[4]/div[1]").text
        bathrooms   = driver.find_element(By.XPATH, "//*[@id='page-content']/div/main/div[2]/article/footer/div[1]/div[4]/div[2]").text
        sleeps      = driver.find_element(By.XPATH, "//*[@id='page-content']/div/main/div[2]/article/footer/div[1]/div[4]/div[3]").text
        images      = driver.find_elements(By.XPATH, "//img[@class='rsImg rsMainSlideImage']")
        images      = [img.get_attribute("src") for img in images]

        return {
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'sleeps': sleeps,
            'images': images,
            }
    finally:
        driver.quit()




APP_NAME = 'Housekeeping Bids'

st.set_page_config(page_title=APP_NAME, page_icon='🏠', layout='centered')

st.image(st.secrets['images']["rd_logo"], width=100)

key = st.query_params.get('bid')

bid_units  = smartsheet_to_dataframe(st.secrets['smartsheet']['sheets']['bid_units'])

bid_ids = bid_units['Bid_ID'].unique().tolist()

if key is None or key not in bid_ids:
    st.warning('It appears you are using an expired link.')
    st.info('Please request the most recent link from **Royal Destinations Housekeeping.**')
else:
    dictionary = {
        'English': {
            'title': 'Housekeeping Bids',
            'description': 'Royal Destinations is seeking bids for housekeeping services for the following properties. Please review the property details and submit your bids below. Please ensure you are available to service the home before placing a bid.',
            'warning': 'Placing a bid does not guarantee that you will be assigned the property.',
            'success': 'Royal Destinations will communicate finalized assignments.',
            'company_name': 'Company name',
            'company_name_placeholder': 'Enter your company name here',
            'interested_communities': 'Select communities you are interested in servicing:',
            'properties_listed': 'Properties are listed East to West and grouped by community.',
            'view_full_listing': 'View Full Listing',
            'bid_amount': 'I would clean',
            'for': 'for',
            'submit_button': 'Submit',
            'submit_success': 'Bids submitted successfully!',
            'no_bids': 'Please place at least one bid before submitting.'
        },
        'Español': {
            'title': 'Ofertas de limpieza',
            'description': 'Royal Destinations está buscando ofertas para servicios de limpieza para las siguientes propiedades. Por favor, revise los detalles de la propiedad y envíe sus ofertas a continuación. Asegúrese de estar disponible para atender la casa antes de hacer una oferta.',
            'warning': 'Hacer una oferta no garantiza que se le asigne la propiedad.',
            'success': 'Royal Destinations comunicará las asignaciones finalizadas.',
            'company_name': 'Nombre de la empresa',
            'company_name_placeholder': 'Ingrese el nombre de su empresa aquí',
            'interested_communities': 'Seleccione las comunidades en las que está interesado en prestar servicios:',
            'properties_listed': 'Las propiedades están listadas de Este a Oeste y agrupadas por comunidad.',
            'view_full_listing': 'Ver listado completo',
            'bid_amount': 'Limpiaría',
            'for': 'por',
            'submit_button': 'Enviar',
            'submit_success': '¡Ofertas enviadas con éxito!',
            'no_bids': 'Por favor, haga al menos una oferta antes de enviar.'
        },
        'Português': {
            'title': 'Ofertas de Limpeza',
            'description': 'A Royal Destinations está buscando ofertas para serviços de limpeza para as seguintes propriedades. Por favor, revise os detalhes da propriedade e envie suas ofertas abaixo. Certifique-se de que está disponível para atender a casa antes de fazer uma oferta.',
            'warning': 'Fazer uma oferta não garante que você será designado para a propriedade.',
            'success': 'A Royal Destinations comunicará as atribuições finalizadas.',
            'company_name': 'Nome da empresa',
            'company_name_placeholder': 'Digite o nome da sua empresa aqui',
            'interested_communities': 'Selecione as comunidades nas quais você tem interesse em prestar serviços:',
            'properties_listed': 'As propriedades estão listadas de Leste a Oeste e agrupadas por comunidade.',
            'view_full_listing': 'Ver listagem completa',
            'bid_amount': 'Eu limparia',
            'for': 'por',
            'submit_button': 'Enviar',
            'submit_success': 'Ofertas enviadas com sucesso!',
            'no_bids': 'Por favor, faça pelo menos uma oferta antes de enviar.'
        }
    }

    language = st.selectbox('Select your language | Seleccione su idioma | Selecione seu idioma', options=['English', 'Español', 'Português'], index=0, key='language')

    st.title(dictionary[language]['title'])
    st.info(dictionary[language]['description'])
    st.warning(dictionary[language]['warning'])
    st.success(dictionary[language]['success'])

    if 'company'   not in st.session_state: st.session_state['company']   = None
    if 'submitted' not in st.session_state: st.session_state['submitted'] = False

    bid_units  = bid_units[bid_units['Bid_ID'] == key]
    units      = smartsheet_to_dataframe(st.secrets['smartsheet']['sheets']['units'])
    df         = pd.merge(units, bid_units, on='Unit_Code', how='right')
    st.session_state['company']    = st.text_input(dictionary[language]['company_name'], value=None, placeholder=dictionary[language]['company_name_placeholder'], key='company_name')

    if st.session_state['company']:

        bids     = []
        area     = ''
        listings = []

        for index, row in df.iterrows():
            listing             = loading_details(row['URL'])
            listing['area']     = row['Area']
            listing['address']  = row['Address']
            listing['order']    = row['Order']
            listing['url']      = row['URL']

            listings.append(listing)
        
        listing_df = pd.DataFrame(listings)
        listing_df = listing_df.sort_values(by=['order'])

        with st.form(key='bids_form', enter_to_submit=False):
            st.caption(dictionary[language]['properties_listed'])
            for index, row in listing_df.iterrows():

                if area != row['area']:
                    area = row['area']
                    st.subheader(f'**{area}**')

                st.write(f'**{row['address']}**')

                l, lm, rm, r = st.columns([1,1,1,2])
                l.write(f'🛏️ {row['bedrooms']}')
                lm.write(f'🛁 {row['bathrooms']}')
                rm.write(f'👥 {row['sleeps']}')
                r.link_button(f'{dictionary[language]['view_full_listing']}', row['url'], type='secondary', width='stretch')

                with st.expander(label="Photos"):
                    for image in row['images']:
                        st.image(image, width='stretch')

                bid = st.number_input(f"{dictionary[language]['bid_amount']} **{row['address']}** {dictionary[language]['for']}:", min_value=0.00, value=0.00, step=5.00, key=f'bid_{index}')
                bids.append(bid)
            
            submit_button = st.form_submit_button(label=dictionary[language]['submit_button'], disabled=st.session_state.submitted, width='stretch', type='primary')
        
        if submit_button:
            if not st.session_state.submitted:
                if sum(bids) == 0:
                    st.warning('Please place at least one bid before submitting.')
                else:
                    st.session_state['submitted']   = True
                    df['Company']                   = st.session_state['company']
                    df['Bid']                       = bids
                    df['Timestamp']                 = pd.Timestamp.now(tz='America/Chicago').strftime('%Y-%m-%d %H:%M:%S')
                    df                              = df[['Unit_Code', 'Company', 'Bid', 'Timestamp']]
                    df                              = df[df['Bid'] > 0]
                    df['Bid_ID']                    = key

                    submit_to_smartsheet(df)

                    st.balloons()
                    st.success(dictionary[language]['submit_success'])
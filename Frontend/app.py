import streamlit as st
import requests

st.title('Жевни говна')

sepal_length = st.slider('Sepal Length', 4.0, 8.0)
sepal_width = st.slider('Sepal Width', 2.0, 5.0)
petal_length = st.slider('petal Length', 1.0, 6.9)
petal_width = st.slider('petal Width', 0.0, 2.5)

# Convert to float
sepal_length = float(sepal_length)
sepal_width = float(sepal_width)
petal_length = float(petal_length)
petal_width = float(petal_width)

input_data = {
    "features": [sepal_length,
                 sepal_width,
                 petal_length,
                 petal_width]

}
st.write(input_data)
response = requests.post('http://backend:8000/predict/', json=input_data)
st.write(response.json())
prediction = response.json()
st.write(f"Predicted Species: {prediction}")

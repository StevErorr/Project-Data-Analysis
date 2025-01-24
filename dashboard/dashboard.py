import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import matplotlib.ticker as ticker
import numpy as np
from babel.numbers import format_currency
import datetime

# Mengatur layout agar lebih lebar
st.set_page_config(layout="wide") 

# Membaca data dan konversi tipe data
try:
    url = "https://raw.githubusercontent.com/StevErorr/Project-Data-Analysis/main/dashboard/all_data.csv"
    df = pd.read_csv(url)

    # Konversi 'DAY_dteday' dan 'dteday' ke datetime
    try:
        df['DAY_dteday'] = pd.to_datetime(df['DAY_dteday'])
    except (KeyError, ValueError): 
        st.warning("Kolom 'DAY_dteday' tidak ditemukan atau formatnya tidak valid. Melewati konversi untuk kolom ini.")
        

    try:
        df['dteday'] = pd.to_datetime(df['dteday'])
    except (KeyError, ValueError): 
        st.warning("Kolom 'dteday' tidak ditemukan atau formatnya tidak valid. Melewati konversi untuk kolom ini.")
        

except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca file: {e}")
    st.stop()  


new_columns = {col: col.replace("DAY_", "") for col in df.columns if col.startswith("DAY_") and col != "DAY_dteday"}
df = df.rename(columns=new_columns)



### AREA LOAD DATA 1
# 1. Membuat Bar Chart 
def create_bar_chart(df, x_col, y_col, title):
    def format_angka(x, pos):
        if x >= 1000000:
            return '%1.0fJ' % (x * 1e-6)
        elif x >= 1000:
            return '%1.0fK' % (x * 1e-3)
        else:
            return '%1.0f' % x
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=x_col, y=y_col, data=df, estimator='sum', ax=ax)
    ax.set_title(title)
    ax.set_xlabel(x_col)
    ax.set_ylabel('Total Jumlah ' + y_col)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_angka))
    plt.tight_layout()
    return fig

try:
    bar_chart = create_bar_chart(df, 'season_new', 'total_rentals', 'Bar Chart Total Penyewaan per Musim')
    #st.pyplot(bar_chart)
except KeyError as e:
    st.error(f"Kolom {e} tidak ditemukan di DataFrame. Pastikan nama kolom sudah benar.")
    st.stop()

# 2. Membuat Box Plot 
def create_box_plot(df, x_col, y_col, title):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(x=x_col, y=y_col, data=df, ax=ax) 
    ax.set_title(title)
    ax.set_xlabel(x_col)
    ax.set_ylabel('Jumlah ' + y_col) 
    plt.tight_layout()
    return fig

try:
    box_plot = create_box_plot(df, 'season_new', 'total_rentals', 'Box Plot Total Penyewaan per Musim')
    #st.pyplot(box_plot)
except KeyError as e:
    st.error(f"Kolom {e} tidak ditemukan di DataFrame. Pastikan nama kolom sudah benar.")
    st.stop()

# 3. Membuat Line Chart 
def create_line_chart(df, x_col, y_col, title):
    fig, ax = plt.subplots(figsize=(8, 6))
    df_grouped = df.groupby(x_col)[y_col].mean()
    ax.plot(df_grouped.index, df_grouped.values, marker='o')
    ax.set_title(title)
    ax.set_xlabel(x_col)
    ax.set_ylabel('Rata-rata ' + y_col)
    plt.tight_layout()
    return fig

try:
    line_chart = create_line_chart(df, 'season_new', 'total_rentals', 'Line Chart Rata-rata Penyewaan per Musim')
    #st.pyplot(line_chart)
except KeyError as e:
    st.error(f"Kolom {e} tidak ditemukan di DataFrame. Pastikan nama kolom sudah benar.")
    st.stop()

# 4. Membuat heatmap
def create_heatmap(df): 
    try:
        plt.figure(figsize=(8, 6))
        pivot_table = df.pivot_table(values='total_rentals', index='season_new', columns=df['DAY_dteday'].dt.day_name(), aggfunc='mean')
        sns.heatmap(pivot_table, annot=True, cmap="YlGnBu", fmt=".0f")
        plt.title('Heatmap Rata-rata Penyewaan per Musim dan Hari dalam Seminggu')
        plt.xlabel('Hari dalam Seminggu')
        plt.ylabel('Musim')
        return plt # Kembalikan objek plt
    except KeyError as e:
        st.error(f"Kolom {e} tidak ditemukan di DataFrame. Pastikan nama kolom sudah benar.")
        return None # Kembalikan None jika terjadi error
    except AttributeError as e:
        st.error(f"Kolom 'DAY_dteday' harus bertipe datetime. Pastikan format datanya benar.")
        return None
    except Exception as e:
        st.error(f"Terjadi kesalahan dalam pembuatan heatmap: {e}")
        return None


### AREA LOAD DATA 2
# 1. Grafik Garis Rata-rata Penyewaan per Jam
def create_line_chart_2(df, x_col, y_col, title):
    fig, ax = plt.subplots(figsize=(12, 8)) 
    hourly_avg = df.groupby('HOUR_hr')[[x_col, y_col]].mean() 
    ax.plot(hourly_avg.index, hourly_avg[x_col], label='Kasual', marker='o', color='lightcoral') 
    ax.plot(hourly_avg.index, hourly_avg[y_col], label='Terdaftar', marker='o', color='lightskyblue') 
    ax.set_xlabel('Jam (hr)')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.set_title(title)
    ax.set_xticks(hourly_avg.index)
    ax.legend()
    ax.grid(True)
    fig.tight_layout() 
    return fig 
    
# 2. Pie Chart proporsi Penyewaan per Jam antara pengguna kasual dan registered
def create_pie_chart_2(df, x_col, y_col, title):
    total_casual = df['HOUR_casual_replaced_upper'].sum()
    total_registered = df['HOUR_registered'].sum()
    total = total_casual + total_registered
    fig, ax = plt.subplots(figsize=(3, 2.8)) 

    if total == 0:
        print("Tidak ada data penyewaan untuk dihitung proporsinya.")
        ax.pie([1, 0], labels=["Tidak ada penyewaan", ""], autopct='', startangle=90) 
        ax.set_title('Proporsi Penyewaan Kasual vs Terdaftar') 
    else:
        proporsi = [total_casual / total * 100, total_registered / total * 100]
        labels = ['Kasual', 'Terdaftar']
        colors = ['lightcoral', 'lightskyblue']
        explode = (0.1, 0)

        ax.pie(proporsi, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90) #menggunakan ax untuk pie
        ax.set_title('Proporsi Penyewaan Kasual vs Terdaftar Per Jam') 
        ax.axis('equal') 
    fig.tight_layout()
    return fig

# 3. Grafik Area Proporsi Penyewaan
def create_graph_area_2(hourly_avg, title):
    if not isinstance(hourly_avg, pd.DataFrame):
        raise TypeError("hourly_avg harus berupa pandas DataFrame")
    if 'HOUR_casual_replaced_upper' not in hourly_avg.columns or 'HOUR_registered' not in hourly_avg.columns:
        raise KeyError("Kolom 'HOUR_casual_replaced_upper' atau 'HOUR_registered' tidak ditemukan di hourly_avg")

    total_hourly = hourly_avg['HOUR_casual_replaced_upper'] + hourly_avg['HOUR_registered']

    # Menangani zero division error dengan np.where
    total_hourly = hourly_avg['HOUR_casual_replaced_upper'] + hourly_avg['HOUR_registered']
    casual_prop = np.where(total_hourly == 0, 0, hourly_avg['HOUR_casual_replaced_upper'] / total_hourly)
    registered_prop = np.where(total_hourly == 0, 0, hourly_avg['HOUR_registered'] / total_hourly)

    plt.figure(figsize=(12, 8))
    plt.stackplot(
        hourly_avg.index,
        [casual_prop, registered_prop],
        labels=['Kasual', 'Terdaftar'],
        colors=['lightcoral', 'lightskyblue']
    )
    plt.xlabel('Jam (hr)')
    plt.ylabel('Proporsi Penyewaan')
    plt.title(title)
    plt.xticks(hourly_avg.index)
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    return plt.gcf()

# 4. Bar Chart Rata-rata Penyewaan Anatar Pengguna Kasual dan Terdaftar
def create_bar_chart_2(df, x_col, y_col, title):
    """
    Fungsi untuk membuat bar chart.
    """
    hourly_avg = df.groupby(x_col)[[y_col[0], y_col[1]]].mean()

    plt.figure(figsize=(12, 8))
    x = np.arange(len(hourly_avg))
    width = 0.35

    plt.bar(x - width/2, hourly_avg[y_col[0]], width, label='Kasual', color='lightcoral')
    plt.bar(x + width/2, hourly_avg[y_col[1]], width, label='Terdaftar', color='lightskyblue')

    plt.xticks(x, hourly_avg.index)
    plt.xlabel('Jam (hr)')
    plt.ylabel('Rata-rata Penyewaan')
    plt.title(title)
    plt.legend()

    for i in x:
        plt.text(x[i] - width/2, hourly_avg[y_col[0]][i], int(hourly_avg[y_col[0]][i]), ha='center', va='bottom')
        plt.text(x[i] + width/2, hourly_avg[y_col[1]][i], int(hourly_avg[y_col[1]][i]), ha='center', va='bottom')

    plt.grid(axis='y', alpha=0.7)
    plt.tight_layout()
    return plt.gcf()
    
    return fig



# AREA CUSTOM SIDE BAR DAN BACKGROUND

# CSS untuk sidebar dan warna tema
st.markdown(
    """
<style>
[data-testid="stSidebar"] {
    width: 20% !important;
    background-color: #87CEFA !important;
    color: white;
    min-height: 100vh; /* Penting */
    display: flex;
    flex-direction: column;
    overflow-y: auto; /* Scrollbar jika konten melebihi tinggi viewport */
    position: relative; /* Untuk konteks positioning footer */
}

.main {
    background-color: #eaf5f8 !important;
}

.sidebar .sidebar-content {
    flex-grow: 1; /* Konten mengisi ruang yang tersedia */
    padding: 20px;
}

.sidebar .footer {
    width: 100%;
    background-color: #64CCC5;
    padding: 10px;
    text-align: center;
    font-size: smaller;
    position: absolute; /* Atau fixed jika ingin selalu terlihat */
    bottom: 0; /* Meletakkan di bawah */
}
</style>
    """,
    unsafe_allow_html=True,
)


## AREA HALAMAN
now = datetime.datetime.now()
st.write(f"Tanggal : {now.strftime('%Y-%m-%d')}")

st.title('ANALISIS DATA *BIKE SHARING*')
st.write("Dataset Bike Sharing menjelaskan data historis penyewaan sepeda dari sistem Capital Bikeshare di Washington D.C., Amerika Serikat, selama dua tahun (2011 dan 2012). Dataset ini dibuat oleh Hadi Fanaee-T dari Laboratorium Kecerdasan Buatan dan Pendukung Keputusan (LIAAD), Universitas Porto.")
st.write("Analisa data ini merupakan proses belajar dalam rangka pengerjaan proyek (Belajar Analisis Data dengan Python).")
st.write("Sumber : https://drive.google.com/file/d/1RaBmV6Q6FYWU4HWZs80Suqd7KQC34diQ/view")


def halaman_pertanyaan_1():
    st.title('Analisis Data Pertanyaan 1')
    st.write("Pertanyaan 1 : Bagaimana musim memengaruhi jumlah penyewaan sepeda? (Pertanyaan ini bertujuan untuk memahami faktor musim yang paling signifikan mempengaruhi permintaan sepeda. Informasi ini krusial untuk manajemen inventaris dan penyesuaian pada musim yang akan datang atau sedang berlangsung). Berikut adalah analisis jumlah penyewa sepeda per musim.")
    
    # Deskripsi
    st.write("Empat kolom dibawah ini merupakan total penyewaan sepeda dari ke empat musim.")

    # Hitung total penyewaan per musim
    total_penyewaan_per_musim = df.groupby('season_new')['total_rentals'].sum().reset_index()

    # Membuat 4 kotak dengan background berbeda menggunakan st.columns
    col1, col2, col3, col4 = st.columns(4)

    # Menggunakan dictionary untuk mempermudah akses
    musim_dict = dict(zip(total_penyewaan_per_musim['season_new'], total_penyewaan_per_musim['total_rentals']))

    #Memformat angka dengan pemisah ribuan.
    def format_number(number):
        return "{:,}".format(number)

    with col1:
        st.markdown(f"""
            <div style="background-color:#FFFF00; padding: 20px; border-radius: 10px; text-align: center;">
                <h3 style="margin-bottom: 10px;">Spring</h3>
                <p style="font-size: 2em; margin: 0;">{format_number(musim_dict.get('Spring', 0))}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div style="background-color:#FFA500; padding: 20px; border-radius: 10px; text-align: center;">
                <h3 style="margin-bottom: 10px;">Summer</h3>
                <p style="font-size: 2em; margin: 0;">{format_number(musim_dict.get('Summer', 0))}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style="background-color:#FFD700; padding: 20px; border-radius: 10px; text-align: center;">
                <h3 style="margin-bottom: 10px;">Fall</h3>
                <p style="font-size: 2em; margin: 0;">{format_number(musim_dict.get('Fall', 0))}</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div style="background-color:#ADD8E6; padding: 20px; border-radius: 10px; text-align: center;">
                <h3 style="margin-bottom: 10px;">Winter</h3>
                <p style="font-size: 2em; margin: 0;">{format_number(musim_dict.get('Winter', 0))}</p>
            </div>
        """, unsafe_allow_html=True)

    # Membuat 2 baris kolom untuk grafik
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row2_col1 = st.columns(1)

    try:
        bar_chart = create_bar_chart(df, 'season_new', 'total_rentals', 'Bar Chart Total Penyewaan per Musim')
        with row1_col1:
            st.header("BAR CHART Total Penyewaan per Musim (Bar)")
            st.pyplot(bar_chart)
    except KeyError as e:
        st.error(f"Kolom {e} tidak ditemukan.")
        st.stop()

    try:
        box_plot = create_box_plot(df, 'season_new', 'total_rentals', 'Box Plot Total Penyewaan per Musim')
        with row1_col2:
            st.header("BOX PLOT Total Penyewaan per Musim ")
            st.pyplot(box_plot)
    except KeyError as e:
        st.error(f"Kolom {e} tidak ditemukan.")
        st.stop()

    try:
        line_chart = create_line_chart(df, 'season_new', 'total_rentals', 'Line Chart Rata-rata Penyewaan per Musim')
        with row1_col3:
            st.header("LINE CHART Rata-rata Penyewaan per Musim")
            st.pyplot(line_chart)
    except KeyError as e:
        st.error(f"Kolom {e} tidak ditemukan.")
        st.stop()

    row2_col1 = st.columns(1)[0] # Perbaikan cara mendapatkan kolom
    heatmap = create_heatmap(df) # Panggil hanya dengan df
    if heatmap:
        with row2_col1: # Gunakan with untuk menempatkan plot di kolom
            st.header("HEAT MAP Rata-rata Penyewaan per Musim")
            st.pyplot(heatmap)

    st.title("KONKLUSI")
    st.write("Perbedaan musim yang ada akan memengaruhi jumlah penyewaan tiap musim.Berdasarkan analisis dari ketiga grafik (box plot, bar chart, dan line chart), dapat ditarik kesimpulan bahwa musim gugur merupakan musim puncak untuk penyewaan sepeda, diikuti oleh musim panas, lalu musim dingin, dan terakhir musim semi dengan permintaan terendah. Perbedaan ini kemungkinan besar dipengaruhi oleh faktor cuaca, di mana musim gugur menawarkan kondisi yang ideal untuk bersepeda. Informasi ini berguna untuk manajemen ketersediaan sepeda, sehingga perlu dioptimalkan untuk memenuhi permintaan tinggi di musim gugur dan mengurangi jumlah sepeda yang tersedia atau menawarkan promosi di musim semi. Hal ini juga dapat memandu strategi pemasaran dan penyesuaian operasional, seperti jam operasional untuk memaksimalkan efisiensi dan pendapatan.")

## HALAMAN 2
def halaman_pertanyaan_2():
    st.title("Pertanyaan 2")
    st.write("Pertanyaan 2 : Bagaimana perbedaan pola penyewaan per jam antara pengguna kasual dan terdaftar? (bertujuan untuk emahami perbedaan antara pengguna kasual dan terdaftar ,penting untuk mengembangkan strategi pemasaran ke target pelanggan yang efektif.). Berikut adalah analisis perbedaan pola penyewaan per jam antara pengguna kasual dan terdaftar") 

# Membuat 2 baris kolom untuk grafik
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    try:
        line_chart2 = create_line_chart_2(df, 'HOUR_casual_replaced_upper', 'HOUR_registered', 'Line Chart Total Penyewaan per Jam')
        with row1_col1:
            st.header("Rata-rata Penyewaan per Jam")
            st.pyplot(line_chart2)
    except KeyError as e:
        st.error(f"Kolom {e} tidak ditemukan.")
        st.stop()

    try:
        bar_chart_2 = create_bar_chart_2(df, 'HOUR_hr', ['HOUR_casual_replaced_upper', 'HOUR_registered'], 'Perbandingan Rata-rata Kasual & Terdaftar per Jam')
        with row1_col2:
            st.header("Rata-rata Penyewaan per Jam")
            st.pyplot(bar_chart_2) 
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}") # Pesan error yang lebih informatif
        st.stop()

    try:
        pie_chart_2 = create_pie_chart_2(df, 'HOUR_hr', ['HOUR_casual_replaced_upper', 'HOUR_registered'], 'Proporsi Penyewaan Sepeda Antara Pengguna Kasual & Terdaftar per Jam')
        with row2_col1:
            st.header("Rata-rata Penyewaan per Jam")
            st.pyplot(pie_chart_2) 
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}") # Pesan error yang lebih informatif
        st.stop()

    try:
    # Pastikan Anda telah menghitung hourly_avg sebelum memanggil fungsi
        hourly_avg = df.groupby('HOUR_hr').agg({'casual': 'sum', 'registered': 'sum'}).rename(columns={'casual': 'HOUR_casual_replaced_upper', 'registered': 'HOUR_registered'})
        graph_area_2 = create_graph_area_2(hourly_avg, 'Proporsi Penyewaan Sepeda Antara Pengguna Kasual & Terdaftar per Jam') # Kirimkan hourly_avg
        with row2_col2: # pastikan row2_col2 sudah didefinisikan sebelumnya
            st.header("Rata-rata Penyewaan per Jam")
            st.pyplot(graph_area_2)
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        st.stop()

    st.title("KONKLUSI")
    st.write("Terdapat pola penyewaan per jam yang berbeda antara pengguna kasual dan terdaftar. Berdasarkan hasil analisa, pengguna terdaftar cenderung menyewa pada jam-jam sibuk dipagi hari (jam 7-8) dan sore hari(jam 16-18). Hal ini menunjukkan pola penyewaan yang mungkin memilki keterkaitan dengan waktu masuk dan pulang kerja. Sedangkan untuk pengguna kasual memiilki pola penyewaan yang tidak terjadi lonjakan signifikan, penyewaan naik perlahan dari mulai pagi hingga sore hari kemudian terjadi penurunan setelah mulai malam.")


## AREA SIDE BAR
# Membuat sidebar
with st.sidebar:
    st.title("ANALISIS PERTANYAAN")
    st.write("Dataset *Bike Sharing* menjelaskan data historis penyewaan sepeda dari sistem Capital Bikeshare di Washington D.C., Amerika Serikat, selama dua tahun (2011 dan 2012).")

    # Inisialisasi session state DI DALAM sidebar
    if "pilihan" not in st.session_state:
        st.session_state.pilihan = "Pertanyaan 1"

    # Selectbox yang tidak bisa diketik
    options = ("Pertanyaan 1", "Pertanyaan 2")
    st.session_state.pilihan = st.selectbox(
        "Analisa sudah dilakukan pada data ini. Silahkan memilih pertanyaan:",
        options=options,
        index=options.index(st.session_state.pilihan) if st.session_state.pilihan in options else 0, # Memastikan index valid
    )

    st.write("Analisa data ini merupakan proses belajar dalam rangka pengerjaan proyek (Belajar Analisis Data dengan Python). " )
    st.caption('Copyright © Dicoding 2023')
    # st.markdown("<div class='footer'>@Copyright by Steven F H</div>", unsafe_allow_html=True)

# Menampilkan halaman berdasarkan pilihan
if st.session_state.pilihan == "Pertanyaan 1": 
    halaman_pertanyaan_1()
elif st.session_state.pilihan == "Pertanyaan 2":
    halaman_pertanyaan_2()

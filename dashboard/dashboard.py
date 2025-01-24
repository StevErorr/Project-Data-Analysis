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


    # Pembersihan dan konversi tipe data (DIPINDAHKAN KE SINI)
    for col in ['HOUR_casual_replaced_upper', 'HOUR_registered', 'HOUR_hr']:
        try:
            df[col] = df[col].astype(str).str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        except KeyError:
            st.warning(f"Kolom {col} tidak ditemukan.")
        except Exception as e:
            st.error(f"Terjadi kesalahan konversi tipe data pada kolom {col}: {e}")
            st.stop()
    

except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca file: {e}")
    st.stop()  


# Menghapus DAY_ pada nama kolom kecuali untuk kolom DAY_dteday
new_columns = {col: col.replace("DAY_", "") for col in df.columns if col.startswith("DAY_") and col != "DAY_dteday"}
df = df.rename(columns=new_columns)

# Fungsi untuk memfilter data berdasarkan musim
def filter_by_season(df, selected_season):
    if selected_season == "All Season":
        return df
    else:
        return df[df['season_new'] == selected_season]

# Fungsi untuk memfilter data berdasarkan jenis pengguna
def filter_by_user_type(df, user_type):
    if user_type == "Semua Pengguna":
        return df
    elif user_type == "Kasual":
        return df[['HOUR_hr', 'HOUR_casual_replaced_upper']] # Hanya kolom kasual
    elif user_type == "Terdaftar":
        return df[['HOUR_hr', 'HOUR_registered']]  # Hanya kolom terdaftar
    else:
        return df # Handle kasus jika ada input yang tidak valid


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



## AREA LOAD DATA 2 
# 1. Line Chart Rata-rata Penyewaan per Jam
def create_line_chart_2(df, x_col, y_col, title, user_type):
    if df.empty:
        st.write("Tidak ada data untuk ditampilkan")
        return None
    if pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
        hourly_avg = df.groupby('HOUR_hr')[[x_col, y_col]].mean()
        fig, ax = plt.subplots(figsize=(12, 8))
        if user_type == "Semua Pengguna":
            ax.plot(hourly_avg.index, hourly_avg['HOUR_casual_replaced_upper'], label='Kasual', marker='o', color='lightcoral')
            ax.plot(hourly_avg.index, hourly_avg['HOUR_registered'], label='Terdaftar', marker='o', color='lightskyblue')
        elif user_type == "Kasual":
            ax.plot(hourly_avg.index, hourly_avg[y_col], label='Kasual', marker='o', color='lightcoral')
        elif user_type == "Terdaftar":
            ax.plot(hourly_avg.index, hourly_avg[y_col], label='Terdaftar', marker='o', color='lightskyblue')
        else:
            ax.plot(hourly_avg.index, hourly_avg[y_col], label=user_type, marker='o')
        ax.set(xlabel='Jam (HOUR_hr)', ylabel='Rata-rata Penyewaan', title=title, xticks=hourly_avg.index)
        ax.legend(); ax.grid(True); fig.tight_layout()
        return fig
    st.write(f"Kolom {x_col} atau {y_col} bukan numerik dan tidak bisa dihitung rata-ratanya.")
    return None

# 2. Bar Chart Rata-rata Penyewaan Anatar Pengguna Kasual dan Terdaftar
def create_bar_chart_2(df, x_col, y_col, title, user_type):
    if df.empty:
        st.write("Tidak ada data untuk ditampilkan")
        return None
    if isinstance(y_col, list):
        if pd.api.types.is_numeric_dtype(df[y_col[0]]) and pd.api.types.is_numeric_dtype(df[y_col[1]]):
            hourly_avg = df.groupby(x_col)[[y_col[0], y_col[1]]].mean()
            x = np.arange(len(hourly_avg)); width = 0.35
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.bar(x - width/2, hourly_avg[y_col[0]], width, label='Kasual', color='lightcoral')
            ax.bar(x + width/2, hourly_avg[y_col[1]], width, label='Terdaftar', color='lightskyblue')
            ax.set(xticks=x, xlabel='Jam (HOUR_hr)', ylabel='Rata-rata Penyewaan', title=title)
            for i in x: ax.text(x[i] - width/2, hourly_avg[y_col[0]][i], int(hourly_avg[y_col[0]][i]), ha='center', va='bottom')
            for i in x: ax.text(x[i] + width/2, hourly_avg[y_col[1]][i], int(hourly_avg[y_col[1]][i]), ha='center', va='bottom')
            ax.legend(); ax.grid(axis='y', alpha=0.7); fig.tight_layout()
            return fig
        st.write(f"Kolom {y_col[0]} atau {y_col[1]} bukan numerik dan tidak bisa dihitung rata-ratanya.")
        return None
    else:
        if pd.api.types.is_numeric_dtype(df[y_col]):
            hourly_avg = df.groupby(x_col)[[y_col]].mean()
            x = np.arange(len(hourly_avg)); width = 0.35
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.bar(x, hourly_avg[y_col], width, label=user_type, color=('lightcoral' if user_type == 'Kasual' else 'lightskyblue'))
            ax.set(xticks=x, xlabel='Jam (HOUR_hr)', ylabel='Rata-rata Penyewaan', title=title)
            for i in x: ax.text(x[i], hourly_avg[y_col][i], int(hourly_avg[y_col][i]), ha='center', va='bottom')
            ax.legend(); ax.grid(axis='y', alpha=0.7); fig.tight_layout()
            return fig
        st.write(f"Kolom {y_col} bukan numerik dan tidak bisa dihitung rata-ratanya.")
        return None

# 3. Pie Chart proporsi Penyewaan per Jam antara pengguna kasual dan registered
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
st.write("Dataset *bike sharing* sebelumnya terbagi menjadi 2 bagian yaitu data **DAY** dan **HOUR**. Data sudah dilakukan proses wranglig dan sudah dianalisa kemudian digabung menjadi all_data.")
st.write("Analisa data ini merupakan proses belajar dalam rangka pengerjaan proyek (Belajar Analisis Data dengan Python).")
st.write("Sumber : https://drive.google.com/file/d/1RaBmV6Q6FYWU4HWZs80Suqd7KQC34diQ/view")


def halaman_pertanyaan_1():
    st.title('Analisis Data Pertanyaan 1 (Menggunakan data **DAY**)')
    st.write("Pertanyaan 1 : Bagaimana musim memengaruhi jumlah penyewaan sepeda? (Pertanyaan ini bertujuan untuk memahami faktor musim yang paling signifikan mempengaruhi permintaan sepeda. Informasi ini krusial untuk manajemen inventaris dan penyesuaian pada musim yang akan datang atau sedang berlangsung). Berikut adalah analisis jumlah penyewa sepeda per musim.")

    # Sidebar untuk memilih musim
    season_options = ["All Season", "Spring", "Summer", "Fall", "Winter"]
    selected_season = st.sidebar.selectbox(" Analisa ini dilakukan berdasarkan musim. Silahkan pilih Musim:", season_options)
    
    # Filter data berdasarkan musim yang dipilih
    filtered_df = filter_by_season(df, selected_season)

    # Hitung total penyewaan (sekarang berdasarkan filter)
    if selected_season == "All Season":
        total_rentals = df['total_rentals'].sum()
    else:
        total_rentals = filtered_df['total_rentals'].sum()

    #Memformat angka dengan pemisah ribuan.
    def format_number(number):
        return "{:,}".format(number)

   # Menampilkan informasi musim dalam satu kolom
    if pd.isna(total_rentals) or total_rentals is None: 
        st.write(f"Tidak ada data penyewaan untuk musim {selected_season}.")
    else:
        st.write("Total Penyewaan untuk Musim yang Dipilih:")
        st.markdown(f"""
            <div style="background-color:{'#ADD8E6' if selected_season == 'Winter' else '#FFFF00' if selected_season == 'Spring' else '#FFA500' if selected_season == 'Summer' else '#FFD700' if selected_season == 'Fall' else '#53adcb'}; padding: 20px; border-radius: 10px; text-align: center;">
                <h2 style="margin-bottom: 20px;">{selected_season}</h2>
                <p style="font-size: 2em; margin: 0;">{format_number(total_rentals)}</p>
            </div>
        """, unsafe_allow_html=True)

    # Membuat kolom untuk grafik 
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row2_col1 = st.columns(1)[0]

    # Bar Chart
    try:
        bar_chart = create_bar_chart(filtered_df, 'season_new', 'total_rentals', f'Bar Chart Total Penyewaan per Musim ({selected_season})') 
        with row1_col1:
            st.header(f"BAR CHART Total Penyewaan per Musim ({selected_season})")
            st.pyplot(bar_chart)
    except KeyError as e:
        st.error(f"Kolom {e} tidak ditemukan.")

    # Box Plot
    try:
        box_plot = create_box_plot(filtered_df, 'season_new', 'total_rentals', f'Box Plot Total Penyewaan per Musim ({selected_season})')
        with row1_col2:
            st.header(f"BOX PLOT Total Penyewaan per Musim ({selected_season})")
            st.pyplot(box_plot)
    except KeyError as e:
        st.error(f"Kolom {e} tidak ditemukan.")

    # Line Chart
    try:
        line_chart = create_line_chart(filtered_df, 'season_new', 'total_rentals', f'Line Chart Rata-rata Penyewaan per Musim ({selected_season})')
        with row1_col3:
            st.header(f"LINE CHART Rata-rata Penyewaan per Musim ({selected_season})")
            st.pyplot(line_chart)
    except KeyError as e:
        st.error(f"Kolom {e} tidak ditemukan.")

    # Heat Map
    heatmap = create_heatmap(filtered_df)
    if heatmap:
        with row2_col1:
            st.header(f"HEAT MAP Rata-rata Penyewaan per Musim ({selected_season})")
            st.pyplot(heatmap)

    st.title("KONKLUSI")
    st.write("Perbedaan musim yang ada akan memengaruhi jumlah penyewaan tiap musim.Berdasarkan analisis dari ketiga grafik (box plot, bar chart, dan line chart), dapat ditarik kesimpulan bahwa musim gugur merupakan musim puncak untuk penyewaan sepeda, diikuti oleh musim panas, lalu musim dingin, dan terakhir musim semi dengan permintaan terendah. Perbedaan ini kemungkinan besar dipengaruhi oleh faktor cuaca, di mana musim gugur menawarkan kondisi yang ideal untuk bersepeda. Informasi ini berguna untuk manajemen ketersediaan sepeda, sehingga perlu dioptimalkan untuk memenuhi permintaan tinggi di musim gugur dan mengurangi jumlah sepeda yang tersedia atau menawarkan promosi di musim semi. Hal ini juga dapat memandu strategi pemasaran dan penyesuaian operasional, seperti jam operasional untuk memaksimalkan efisiensi dan pendapatan.")


## HALAMAN 2
def halaman_pertanyaan_2():
    st.title("Pertanyaan 2 (Menggunakan data **HOUR**)")
    st.write("Pertanyaan 2 : Bagaimana perbedaan pola penyewaan per jam antara pengguna kasual dan terdaftar? (bertujuan untuk Memahami perbedaan antara pengguna kasual dan terdaftar ,penting untuk mengembangkan strategi pemasaran ke target pelanggan yang efektif.). Berikut adalah analisis perbedaan pola penyewaan per jam antara pengguna kasual dan terdaftar") 

    # Sidebar untuk memilih jenis pengguna
    user_type = st.sidebar.selectbox("Pilih Jenis Pengguna:", ["Semua Pengguna", "Kasual", "Terdaftar"])

    # Filter data berdasarkan jenis pengguna
    filtered_df = filter_by_user_type(df, user_type)

    # Pengecekan penting: Apakah DataFrame kosong?
    if filtered_df.empty:
        st.warning(f"Tidak ada data untuk jenis pengguna: {user_type}")
        return  # Hentikan eksekusi fungsi jika DataFrame kosong

    # Reset index jika diperlukan (kemungkinan kecil dibutuhkan sekarang)
    filtered_df = filtered_df.reset_index(drop=True)

    # Membuat kolom untuk grafik
    row1_col1, row1_col2 = st.columns(2)
    row2_col1 = st.columns(1)[0]

    # Line Chart
    try:
        if user_type == "Semua Pengguna":
            line_chart2 = create_line_chart_2(filtered_df, 'HOUR_casual_replaced_upper', 'HOUR_registered', 'Line Chart Rata-rata Penyewaan Pengguna Kasual & Terdaftar per Jam', user_type)
        elif user_type == "Kasual":
            line_chart2 = create_line_chart_2(filtered_df, 'HOUR_casual_replaced_upper', 'HOUR_casual_replaced_upper', 'Line Chart Rata-rata Penyewaan Pengguna Kasual per Jam', user_type)
        elif user_type == "Terdaftar":
            line_chart2 = create_line_chart_2(filtered_df, 'HOUR_registered', 'HOUR_registered', 'Line Chart Rata-rata Penyewaan Pengguna Terdaftar per Jam ', user_type)
        with row1_col1:
            st.header(f"Rata-rata Penyewaan per Jam ({user_type})")
            st.pyplot(line_chart2)
    except KeyError as e:
        st.error(f"Kolom {e} tidak ditemukan.")
        st.stop()


    # Bar Chart    
    try:
        if user_type == "Semua Pengguna":
            bar_chart_2 = create_bar_chart_2(df, 'HOUR_hr', ['HOUR_casual_replaced_upper', 'HOUR_registered'], 'Bar Chart Rata-rata Penyewaan Pengguna Kasual & Terdaftar per Jam', user_type)
        elif user_type == "Kasual":
            bar_chart_2 = create_bar_chart_2(filtered_df, 'HOUR_hr', 'HOUR_casual_replaced_upper', 'Bar Chart Rata-rata Penyewaan Pengguna Kasual per Jam', user_type)
        elif user_type == "Terdaftar":
            bar_chart_2 = create_bar_chart_2(filtered_df, 'HOUR_hr', 'HOUR_registered', 'Bar Chart Rata-rata Penyewaan Pengguna Terdaftar per Jam', user_type)
        with row1_col2:
            st.header(f"Rata-rata Penyewaan per Jam ({user_type})")
            st.pyplot(bar_chart_2)
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
        st.stop()

    # Pie Chart
    try:
        pie_chart_2 = create_pie_chart_2(df, 'HOUR_hr', ['HOUR_casual_replaced_upper', 'HOUR_registered'], 'Proporsi Penyewaan Sepeda Antara Pengguna Kasual & Terdaftar per Jam')
        with row2_col1:
            st.header("Proporsi Total Penyewa per Jam")
            st.pyplot(pie_chart_2)
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
        "Analisa yang dilakukan pada data ini, dilakukan berdasarkan pertanyaan yang ada. Silahkan memilih pertanyaan:",
        options=options,
        index=options.index(st.session_state.pilihan) if st.session_state.pilihan in options else 0, 
    )

    st.write("Analisa data ini merupakan proses belajar dalam rangka pengerjaan proyek (Belajar Analisis Data dengan Python). " )
    st.caption('Copyright © Steven F H 2025')

# Routing halaman (tidak berubah)
if st.session_state.pilihan == "Pertanyaan 1":
    halaman_pertanyaan_1()
elif st.session_state.pilihan == "Pertanyaan 2":
    halaman_pertanyaan_2()


st.caption('Copyright © Steven F H 2025')

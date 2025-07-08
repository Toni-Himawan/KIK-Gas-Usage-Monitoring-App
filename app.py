import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

st.set_page_config(layout="wide")  # Layout full width supaya tampilan lebar

st.title("KIK Monthly Usage of 12 Tenants")

# Membuat 2 kolom: kiri untuk uploader, kanan untuk konten
col1, col2 = st.columns([1, 3])  # Kolom kiri lebih kecil dari kanan

with col1:
    uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

with col2:
    if uploaded_file:
        df_gas = pd.read_excel(uploaded_file, sheet_name="Pemakaian Gas")
        df_jisdor = pd.read_excel(uploaded_file, sheet_name="JISDOR")

        bulan_asli = df_gas.columns[1:]
        bulan_label = []
        for b in bulan_asli:
            try:
                tgl = pd.to_datetime(b)
                bulan_label.append(tgl.strftime('%B').upper() + ' ' + str(tgl.year))
            except:
                bulan_label.append(str(b))

        mapping_kolom = dict(zip(bulan_asli, bulan_label))
        reverse_mapping = {v: k for k, v in mapping_kolom.items()}

        df_gas_rename = df_gas.rename(columns=mapping_kolom)

        st.subheader("Data Pemakaian Gas")
        st.dataframe(df_gas_rename)

        selected_label = st.selectbox("Pilih Bulan", bulan_label)

        if selected_label:
            selected_bulan = reverse_mapping[selected_label]

            st.subheader(f"Grafik Pemakaian Gas {selected_label}")

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(df_gas["Tenant"], df_gas[selected_bulan])

            ax.set_xlabel("Tenant", fontsize=10)
            ax.set_ylabel("Pemakaian (MMBTU)", fontsize=10)
            ax.set_title(f"Pemakaian Gas - {selected_label}", fontsize=12)

            plt.xticks(rotation=90, fontsize=8)
            plt.yticks(fontsize=8)

            plt.tight_layout()
            st.pyplot(fig)

            max_idx = df_gas[selected_bulan].idxmax()
            min_idx = df_gas[selected_bulan].idxmin()

            tenant_max = df_gas.loc[max_idx, "Tenant"]
            value_max = round(df_gas.loc[max_idx, selected_bulan], 2)

            tenant_min = df_gas.loc[min_idx, "Tenant"]
            value_min = round(df_gas.loc[min_idx, selected_bulan], 2)

            st.subheader(f"Tenant dengan Pemakaian Gas Tertinggi dan Terendah {selected_label}")
            st.markdown(f"<span style='font-size:20px;'>🔺 Tertinggi: <b>{tenant_max}</b> = {value_max:.2f} MMBTU</span>", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size:20px;'>🔻 Terendah: <b>{tenant_min}</b> = {value_min:.2f} MMBTU</span>", unsafe_allow_html=True)

            try:
                kurs = float(df_jisdor.loc[df_jisdor["Bulan"] == selected_bulan, "Kurs"].values[0])
                total_pemakaian = round(df_gas[selected_bulan].sum(), 2)
                nilai_usd = total_pemakaian * 0.6 * kurs
                pemanfaatan = round(nilai_usd - 73000000, 2)
                st.subheader(f"Total Nilai Rekonsiliasi {selected_label}")
                st.markdown(f"<span style='font-size:20px;'>Total Pemakaian: <b>{total_pemakaian:.2f} MMBTU</b></span>", unsafe_allow_html=True)
                st.markdown(f"<span style='font-size:20px;'>Nilai Rekonsiliasi: <b>Rp {pemanfaatan:,.0f}</b></span>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Gagal menghitung pemanfaatan: {e}")

            # Garis pemisah antar bagian supaya pembaca jelas ini data berbeda
            st.markdown("<hr style='border: 2px solid #333; margin: 30px 0;'>", unsafe_allow_html=True)

        # Menambahkan tombol untuk generate laporan PDF
        if st.button("Generate Laporan PDF"):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Menambahkan judul
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="Laporan Pemakaian Gas Tenant KIK - Juni 2025", ln=True, align="C")
            pdf.ln(10)

            # Menambahkan data pemakaian gas
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Data Pemakaian Gas:", ln=True)
            for index, row in df_gas.iterrows():
                pdf.cell(200, 10, txt=f"{row['Tenant']}: {row[selected_bulan]} MMBTU", ln=True)

            pdf.ln(10)

            # Menambahkan grafik
            st.pyplot(fig)  # Mungkin perlu ditangani dengan cara lain untuk menyimpan grafik sebagai gambar

            # Menyimpan PDF
            pdf_output_path = "/tmp/laporan_pemakaian_gas.pdf"
            pdf.output(pdf_output_path)

            # Memberikan link untuk mengunduh laporan
            with open(pdf_output_path, "rb") as f:
                st.download_button("Unduh Laporan PDF", f, file_name="laporan_pemakaian_gas.pdf")

        st.markdown("<hr style='border: 2px solid #333; margin: 30px 0;'>", unsafe_allow_html=True)

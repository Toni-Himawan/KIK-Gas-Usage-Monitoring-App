import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

        bulan_2025 = [b for b in bulan_asli if pd.to_datetime(b, errors='coerce') is not pd.NaT and pd.to_datetime(b).year == 2025]
        bulan_tersedia = []
        for b in bulan_2025:
            try:
                if not df_gas[b].isnull().all() and not df_jisdor[df_jisdor["Bulan"] == b].empty:
                    bulan_tersedia.append(b)
            except:
                continue

        label_tersedia = [mapping_kolom[b] for b in bulan_tersedia]

        if label_tersedia:
            st.subheader(f"Grafik Pemakaian Gas sampai {label_tersedia[-1]}")

            df_berjalan = df_gas[["Tenant"] + bulan_tersedia].copy()

            fig2, ax2 = plt.subplots(figsize=(8, 4))
            for i, row in df_berjalan.iterrows():
                ax2.plot(label_tersedia, row[bulan_tersedia], marker='o', label=row["Tenant"])

            ax2.set_xlabel("Bulan", fontsize=10)
            ax2.set_ylabel("Pemakaian (MMBTU)", fontsize=10)
            ax2.set_title(f"Pemakaian Gas Januari – {label_tersedia[-1]} 2025", fontsize=12)
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
            plt.xticks(rotation=45, fontsize=8)
            plt.yticks(fontsize=8)
            plt.tight_layout()
            st.pyplot(fig2)
        else:
            st.info("Data bulan untuk tahun 2025 belum tersedia atau kosong.")

        st.subheader("Total Kumulatif Nilai Rekonsiliasi Selama 2025")

        df_rekon = pd.DataFrame()
        bulan_label_rekon = []
        for b in bulan_tersedia:
            try:
                kurs = float(df_jisdor.loc[df_jisdor["Bulan"] == b, "Kurs"].values[0])
                rekon = df_gas[b] * 0.6 * kurs - (73000000 / len(df_gas))
                df_rekon[mapping_kolom[b]] = rekon
                bulan_label_rekon.append(mapping_kolom[b])
            except:
                continue
        df_rekon["Tenant"] = df_gas["Tenant"]
        df_rekon = df_rekon.set_index("Tenant")

        total_kumulatif = df_rekon.sum().sum()

        if bulan_label_rekon:
            st.markdown(f"**_(sampai dengan bulan {bulan_label_rekon[-1]})_**")

        st.markdown(
            f"<h2 style='color:red; font-weight:bold;'>Rp{total_kumulatif:,.0f}</h2>",
            unsafe_allow_html=True
        ). 

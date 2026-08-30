/**
 * İkonlar — satır içi SVG, dış bağımlılık yok.
 *
 * İkon hiçbir yerde tek başına anlam taşımaz; her zaman bir metin
 * etiketinin yanında durur (ana talimat Bölüm 9.3). `aria-hidden` ile
 * ekran okuyuculardan gizlenir çünkü anlamı komşu metin taşır.
 */
type Ozellik = { boyut?: number; className?: string }

function Sarmal({ boyut = 16, className = '', children }: Ozellik & {
  children: React.ReactNode
}) {
  return (
    <svg
      width={boyut} height={boyut} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={1.8}
      strokeLinecap="round" strokeLinejoin="round"
      aria-hidden className={`shrink-0 ${className}`}
    >
      {children}
    </svg>
  )
}

export const Ikon = {
  Alan: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M3 7l6-3 6 3 6-3v13l-6 3-6-3-6 3z" />
      <path d="M9 4v13M15 7v13" />
    </Sarmal>
  ),
  Harita: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z" />
      <circle cx="12" cy="10" r="2.5" />
    </Sarmal>
  ),
  Kuyruk: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M4 6h16M4 12h16M4 18h10" />
      <circle cx="19" cy="18" r="2.5" />
    </Sarmal>
  ),
  Gecmis: (p: Ozellik) => (
    <Sarmal {...p}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3.5 2" />
    </Sarmal>
  ),
  Kullanici: (p: Ozellik) => (
    <Sarmal {...p}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c0-4 3.6-6 8-6s8 2 8 6" />
    </Sarmal>
  ),
  Yukle: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M12 16V4M7.5 8.5L12 4l4.5 4.5" />
      <path d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" />
    </Sarmal>
  ),
  Onayla: (p: Ozellik) => (
    <Sarmal {...p}><path d="M4.5 12.5l5 5 10-11" /></Sarmal>
  ),
  Duzelt: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M4 20l4-1 11-11a2 2 0 0 0-3-3L5 16z" />
    </Sarmal>
  ),
  Belirsiz: (p: Ozellik) => (
    <Sarmal {...p}>
      <circle cx="12" cy="12" r="9" />
      <path d="M9.5 9.5a2.6 2.6 0 1 1 3.4 2.5c-.6.2-.9.8-.9 1.4v.6" />
      <path d="M12 17.2v.01" />
    </Sarmal>
  ),
  Bekle: (p: Ozellik) => (
    <Sarmal {...p}><circle cx="12" cy="12" r="9" strokeDasharray="3 3" /></Sarmal>
  ),
  Uyari: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M12 4l9 16H3z" />
      <path d="M12 10v4M12 17.5v.01" />
    </Sarmal>
  ),
  Terazi: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M12 4v16M7 20h10" />
      <path d="M4 9h16M4 9l-2 5a3 3 0 0 0 6 0zM20 9l2 5a3 3 0 0 1-6 0z" />
    </Sarmal>
  ),
  Lab: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M9 3v6.5L4.5 18a2 2 0 0 0 1.8 3h11.4a2 2 0 0 0 1.8-3L15 9.5V3" />
      <path d="M8 3h8M7.5 14h9" />
    </Sarmal>
  ),
  Cikis: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M10 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5" />
      <path d="M16 16l5-4-5-4M21 12H10" />
    </Sarmal>
  ),
  Geri: (p: Ozellik) => (
    <Sarmal {...p}><path d="M15 5l-7 7 7 7" /></Sarmal>
  ),
  Ara: (p: Ozellik) => (
    <Sarmal {...p}>
      <circle cx="11" cy="11" r="6.5" /><path d="M16 16l4.5 4.5" />
    </Sarmal>
  ),
  Gunes: (p: Ozellik) => (
    <Sarmal {...p}>
      <circle cx="12" cy="12" r="4.2" />
      <path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.2 5.2l1.4 1.4M17.4 17.4l1.4 1.4M18.8 5.2l-1.4 1.4M6.6 17.4l-1.4 1.4" />
    </Sarmal>
  ),
  Ay: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z" />
    </Sarmal>
  ),
  Foto: (p: Ozellik) => (
    <Sarmal {...p}>
      <rect x="3" y="6" width="18" height="14" rx="2" />
      <circle cx="12" cy="13" r="3.4" />
      <path d="M8 6l1.5-2h5L16 6" />
    </Sarmal>
  ),
  Grafik: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" />
    </Sarmal>
  ),
  Goz: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z" />
      <circle cx="12" cy="12" r="3" />
    </Sarmal>
  ),
  GozKapali: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M4 5l16 14" />
      <path d="M9.6 6.2A10.9 10.9 0 0 1 12 5.5c6.4 0 10 6.5 10 6.5a18 18 0 0 1-3.3 4" />
      <path d="M6.4 8.2A17.6 17.6 0 0 0 2 12s3.6 6.5 10 6.5a10.6 10.6 0 0 0 3.9-.7" />
      <path d="M9.9 10.2a3 3 0 0 0 4.1 4.2" />
    </Sarmal>
  ),
  /** Sahte model servisi rozeti — uyarı üçgeni değil, "laboratuvar" işareti. */
  Sahte: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M10 3v6.5L4.6 18a1.8 1.8 0 0 0 1.5 2.8h11.8a1.8 1.8 0 0 0 1.5-2.8L14 9.5V3" />
      <path d="M8.5 3h7M7.6 14h8.8" />
    </Sarmal>
  ),
  Baglanti: (p: Ozellik) => (
    <Sarmal {...p}>
      <path d="M5 12.5a9.5 9.5 0 0 1 14 0M8 16a5 5 0 0 1 8 0" />
      <circle cx="12" cy="19.5" r="1" />
      <path d="M3 3l18 18" />
    </Sarmal>
  ),
}

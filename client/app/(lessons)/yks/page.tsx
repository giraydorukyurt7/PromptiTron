"use client";

import React, { useState, JSX } from "react";
import {
    ChevronDown,
    ChevronRight,
    BookOpen,
    Target,
    Book,
    Hash,
} from "lucide-react";
import { useRouter } from "next/navigation";

// Tip tanımlamaları - Felsefe yapısı için
interface Aciklama {
    [key: string]: string;
}

interface FeKazanim {
    baslik: string;
    aciklama: Aciklama;
}

interface FeKonu {
    [kazanimKey: string]: FeKazanim;
}

interface FeSinif {
    [konuKey: string]: FeKonu;
}

interface FeDers {
    [sinifKey: string]: FeSinif;
}

// Tip tanımlamaları - Kimya yapısı için
interface KiKazanim {
    baslik: string;
    aciklama?: Aciklama;
    anahtar_kavramlar?: string;
    alt?: any;
}

interface KiKonu {
    baslik: string;
    anahtar_kavramlar?: string;
    alt: {
        [key: string]: KiKazanim | KiAltKonu;
    };
}

interface KiAltKonu {
    baslik: string;
    anahtar_kavramlar?: string;
    alt?: {
        [key: string]: KiKazanim | KiAltKonu;
    };
}

interface KiSinif {
    alt: {
        [key: string]: KiKonu;
    };
}

interface KiDers {
    [sinifKey: string]: KiSinif;
}

// Genel yapı
interface YKSData {
    yks: {
        [dersKey: string]: FeDers | KiDers;
    };
}

// Ders listesi
const YKS_DERSLERI = [
    {
        name: "matematik",
        displayName: "Matematik",
        file: "/kazanimlar/kazanimlar_matematik.json",
    },
    {
        name: "felsefe",
        displayName: "Felsefe",
        file: "/kazanimlar/kazanimlar_felsefe.json",
    },
    {
        name: "biyoloji",
        displayName: "Biyoloji",
        file: "/kazanimlar/kazanimlar_biyoloji.json",
    },
    {
        name: "cografya",
        displayName: "Coğrafya",
        file: "/kazanimlar/kazanimlar_cografya.json",
    },
    {
        name: "din_kulturu",
        displayName: "Din Kültürü",
        file: "/kazanimlar/kazanimlar_din_kulturu.json",
    },
    {
        name: "fizik",
        displayName: "Fizik",
        file: "/kazanimlar/kazanimlar_fizik.json",
    },
    {
        name: "inkilap",
        displayName: "İnkılap Tarihi",
        file: "/kazanimlar/kazanimlar_inkilap_ve_ataturkculuk.json",
    },
    {
        name: "kimya",
        displayName: "Kimya",
        file: "/kazanimlar/kazanimlar_kimya.json",
    },
    {
        name: "tarih",
        displayName: "Tarih",
        file: "/kazanimlar/kazanimlar_tarih.json",
    },
    {
        name: "turk_dili_ve_edebiyatı",
        displayName: "Türk Dili ve Edebiyatı",
        file: "/kazanimlar/kazanimlar_turk_dili_ve_edebiyati.json",
    },
];


interface CheckboxSelection {
    id: string;
    type: "ders" | "sinif" | "konu" | "kazanim" | "aciklama";
    ders: string;
    sinif?: string;
    konu?: string;
    kazanim?: string;
    aciklama?: string;
    title: string;
    path: string;
}

const YKSKazanimlar: React.FC = () => {
    const router = useRouter();
    const [selectedDers, setSelectedDers] = useState<string>("");
    const [dersData, setDersData] = useState<YKSData | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string>("");
    const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
    const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());
    const [showSelectionPanel, setShowSelectionPanel] = useState<boolean>(true);

    // JSON dosyasını yükle
    const loadDersData = async (dersName: string) => {
        setLoading(true);
        setError("");
        try {
            const ders = YKS_DERSLERI.find((d) => d.name === dersName);
            if (!ders) {
                throw new Error("Ders bulunamadı");
            }

            const response = await fetch(ders.file);
            if (!response.ok) {
                throw new Error("Veri yüklenemedi");
            }

            const data: YKSData = await response.json();
            setDersData(data);
        } catch (err) {
            setError("Veri yüklenirken hata oluştu");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    // Ders yapısını kontrol et (Felsefe mi Kimya tipi mi)
    const isDersKimyaType = (dersData: any, dersName: string): boolean => {
        if (!dersData?.yks?.[dersName]) return false;
        const firstSinif = Object.values(dersData.yks[dersName])[0] as any;
        return (
            firstSinif && typeof firstSinif === "object" && "alt" in firstSinif
        );
    };

    // Ders seçildiğinde
    const handleDersSelect = (dersName: string) => {
        setSelectedDers(dersName);
        setExpandedItems(new Set());
        loadDersData(dersName);
    };

    // Genişletme/daraltma
    const toggleExpanded = (key: string) => {
        const newExpanded = new Set(expandedItems);
        if (newExpanded.has(key)) {
            newExpanded.delete(key);
        } else {
            newExpanded.add(key);
        }
        setExpandedItems(newExpanded);
    };


    // Checkbox işlemleri
    const handleCheckboxChange = (itemId: string, checked: boolean) => {
        const newCheckedItems = new Set(checkedItems);
        if (checked) {
            newCheckedItems.add(itemId);
        } else {
            newCheckedItems.delete(itemId);
        }
        setCheckedItems(newCheckedItems);
    };

    const clearAllSelections = () => {
        setCheckedItems(new Set());
    };

    const getSelectedItemsData = (): CheckboxSelection[] => {
        const selectedData: CheckboxSelection[] = [];
        
        if (!dersData || !selectedDers) return selectedData;

        // Seçilen her checkbox ID'sini analiz et
        Array.from(checkedItems).forEach(itemId => {
            const parts = itemId.split('-');
            
            if (parts.length >= 2) {
                const ders = parts[0];
                const sinif = parts[1];
                
                if (parts.length === 2) {
                    // Sınıf seçimi
                    selectedData.push({
                        id: itemId,
                        type: "sinif",
                        ders,
                        sinif,
                        title: `${sinif}. Sınıf`,
                        path: itemId
                    });
                } else if (parts.length === 3) {
                    // Konu seçimi (Felsefe tipi) veya Ana Konu (Kimya tipi)
                    const konuKey = parts[2];
                    let konuTitle = konuKey;
                    let konuValue = konuKey; // Konu içeriği
                    
                    try {
                        const dersContent = dersData.yks[ders] as any;
                        const sinifContent = dersContent?.[sinif];
                        
                        if (isDersKimyaType(dersData, ders)) {
                            // Kimya tipi
                            if (sinifContent?.alt?.[konuKey]) {
                                konuTitle = sinifContent.alt[konuKey].baslik || konuKey;
                                konuValue = konuTitle; // Başlığı konu olarak kullan
                            }
                        } else {
                            // Felsefe tipi - konular direkt sinif altında
                            konuValue = konuKey; // Felsefe'de konu key'leri zaten isimler
                            konuTitle = konuKey;
                        }
                    } catch (e) {
                        console.warn('Konu bilgisi bulunamadı:', itemId);
                    }
                    
                    selectedData.push({
                        id: itemId,
                        type: "konu",
                        ders,
                        sinif,
                        konu: konuValue,
                        title: konuTitle,
                        path: itemId
                    });
                } else if (parts.length >= 4) {
                    // Kazanım seçimi
                    const konuKey = parts[2];
                    const kazanimKey = parts[3];
                    let title = kazanimKey;
                    let konuValue = konuKey;
                    let kazanimValue = kazanimKey;
                    
                    // Başlık bilgisini almaya çalış
                    try {
                        const dersContent = dersData.yks[ders] as any;
                        const sinifContent = dersContent?.[sinif];
                        
                        if (isDersKimyaType(dersData, ders)) {
                            // Kimya tipi
                            if (sinifContent?.alt?.[konuKey]) {
                                // Konu başlığını al
                                konuValue = sinifContent.alt[konuKey].baslik || konuKey;
                                
                                const findItemByPath = (item: any, pathParts: string[], index: number): any => {
                                    if (index >= pathParts.length - 1) return item;
                                    const nextKey = pathParts[index + 1];
                                    return item.alt?.[nextKey] ? findItemByPath(item.alt[nextKey], pathParts, index + 1) : null;
                                };
                                
                                const item = findItemByPath(sinifContent.alt[konuKey], parts, 2);
                                if (item?.baslik) {
                                    title = item.baslik;
                                    kazanimValue = item.baslik; // Kazanım başlığını kullan
                                }
                            }
                        } else {
                            // Felsefe tipi
                            konuValue = konuKey; // Felsefe'de konu key'leri zaten isimler
                            if (sinifContent?.[konuKey]?.[kazanimKey]) {
                                const kazanimData = sinifContent[konuKey][kazanimKey];
                                if (kazanimData?.baslik) {
                                    title = kazanimData.baslik;
                                    kazanimValue = kazanimData.baslik; // Kazanım başlığını kullan
                                }
                            }
                        }
                    } catch (e) {
                        console.warn('Title bulunamadı:', itemId);
                    }
                    
                    selectedData.push({
                        id: itemId,
                        type: "kazanim",
                        ders,
                        sinif,
                        konu: konuValue,
                        kazanim: kazanimValue,
                        title,
                        path: itemId
                    });
                }
            }
        });

        return selectedData;
    };

    // Müfredat aksiyonları işleyicisi
    const handleCurriculumAction = (action: string) => {
        const selectedData = getSelectedItemsData();
        
        if (selectedData.length === 0) {
            alert("Lütfen en az bir konu seçin");
            return;
        }

        // Seçilen konular için veri formatını hazırla - müfredat içeriğini de ekle
        const topicsData = selectedData.map(item => {
            // Path'i parse ederek orijinal key'leri alalım
            const pathParts = item.path.split('-');
            const originalDers = pathParts[0];
            const originalSinif = pathParts[1];
            const originalKonuKey = pathParts[2] || "";
            const originalKazanimKey = pathParts[3] || "";
            
            const topicData: any = {
                ders: item.ders, // Ders adı (kimya, felsefe vb.)
                sinif: item.sinif || "",
                konu: item.konu || "", // Konu başlığı
                kazanim: item.kazanim || "", // Kazanım başlığı
                title: item.title,
                aciklama: "", // Açıklama içeriğini alacağız
                path: item.path,
                type: item.type
            };

            // Müfredat içeriğini ekle - orijinal key'leri kullanarak
            if (dersData && originalDers) {
                const dersContent = dersData.yks[originalDers] as any;
                if (dersContent && originalSinif) {
                    const sinifContent = dersContent[originalSinif];
                    
                    if (isDersKimyaType(dersData, originalDers)) {
                        // Kimya tipi - alt yapısından içeriği al
                        if (sinifContent?.alt && originalKonuKey) {
                            const konuContent = sinifContent.alt[originalKonuKey];
                            if (konuContent) {
                                // Konu seviyesindeki bilgileri ekle
                                topicData.mufredat_icerigi = {
                                    baslik: konuContent.baslik,
                                    anahtar_kavramlar: konuContent.anahtar_kavramlar
                                };
                                
                                // Kazanım seviyesindeki içeriği de ekle
                                if (originalKazanimKey && konuContent.alt) {
                                    // Nested yapıyı dolaş
                                    const findKazanim = (obj: any, remainingPath: string[]): any => {
                                        if (remainingPath.length === 0) return obj;
                                        const nextKey = remainingPath[0];
                                        if (obj.alt && obj.alt[nextKey]) {
                                            return findKazanim(obj.alt[nextKey], remainingPath.slice(1));
                                        }
                                        return null;
                                    };
                                    
                                    // Path'in konu sonrası kısmını al
                                    const kazanimPath = pathParts.slice(3);
                                    const kazanimContent = findKazanim(konuContent, kazanimPath);
                                    
                                    if (kazanimContent) {
                                        topicData.kazanim_detay = {
                                            baslik: kazanimContent.baslik,
                                            anahtar_kavramlar: kazanimContent.anahtar_kavramlar,
                                            aciklama: kazanimContent.aciklama
                                        };
                                        
                                        // Açıklamaları birleştir
                                        if (kazanimContent.aciklama && typeof kazanimContent.aciklama === 'object') {
                                            const aciklamalar = Object.entries(kazanimContent.aciklama)
                                                .map(([key, value]) => `${key}) ${value}`)
                                                .join(' ');
                                            topicData.aciklama = aciklamalar;
                                        }
                                    }
                                }
                            }
                        }
                    } else {
                        // Felsefe tipi
                        if (sinifContent && originalKonuKey) {
                            const konuContent = sinifContent[originalKonuKey];
                            if (konuContent && originalKazanimKey) {
                                const kazanimContent = konuContent[originalKazanimKey];
                                if (kazanimContent) {
                                    topicData.mufredat_icerigi = {
                                        baslik: kazanimContent.baslik,
                                        aciklama: kazanimContent.aciklama
                                    };
                                    
                                    // Açıklamaları birleştir
                                    if (kazanimContent.aciklama && typeof kazanimContent.aciklama === 'object') {
                                        const aciklamalar = Object.entries(kazanimContent.aciklama)
                                            .map(([key, value]) => `${key}) ${value}`)
                                            .join(' ');
                                        topicData.aciklama = aciklamalar;
                                    }
                                }
                            }
                        }
                    }
                }
            }

            return topicData;
        });

        // Session storage'a veriyi kaydet
        sessionStorage.setItem('selectedCurriculumTopics', JSON.stringify(topicsData));
        sessionStorage.setItem('curriculumActionType', action);

        // İlgili sayfaya yönlendir
        switch (action) {
            case 'questions':
                router.push('/curriculum/questions');
                break;
            case 'summary':
                router.push('/curriculum/summary');
                break;
            case 'concept-map':
                router.push('/curriculum/concept-map');
                break;
            case 'explanation':
                router.push('/curriculum/explanation');
                break;
            case 'ai-chat':
                router.push('/curriculum/ai-chat');
                break;
            case 'socratic':
                router.push('/curriculum/socratic');
                break;
            default:
                console.error('Unknown action:', action);
        }
    };

    // Felsefe tipi için render fonksiyonları
    const renderFeAciklama = (aciklama: Aciklama, parentKey: string) => {
        return (
            <div className="ml-6 space-y-2">
                {Object.entries(aciklama).map(([key, value]) => (
                    <div
                        key={`${parentKey}-${key}`}
                        className="p-3 rounded-lg border cursor-pointer transition-colors bg-gray-50 border-gray-200 hover:bg-gray-100"
                        onClick={() => {
                            // Tıklamalarda artık handleSelect yok
                        }}
                    >
                        <div className="flex items-start gap-2">
                            <input
                                type="checkbox"
                                checked={checkedItems.has(`${selectedDers}-${parentKey}-${key}`)}
                                onChange={(e) => {
                                    e.stopPropagation();
                                    handleCheckboxChange(`${selectedDers}-${parentKey}-${key}`, e.target.checked);
                                }}
                                className="mt-1 flex-shrink-0"
                            />
                            <span className="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-1 rounded">
                                {key}
                            </span>
                            <p className="text-sm text-gray-700 flex-1">
                                {value}
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    const renderFeKazanim = (
        kazanim: FeKazanim,
        kazanimKey: string,
        parentKey: string,
    ) => {
        const fullKey = `${parentKey}-${kazanimKey}`;
        const isExpanded = expandedItems.has(fullKey);

        return (
            <div key={kazanimKey} className="ml-4">
                <div
                    className="p-3 rounded-lg border cursor-pointer transition-colors bg-white border-gray-200 hover:bg-gray-50"
                >
                    <div
                        className="flex items-center gap-2"
                        onClick={() => {
                            toggleExpanded(fullKey);
                        }}
                    >
                        <input
                            type="checkbox"
                            checked={checkedItems.has(fullKey)}
                            onChange={(e) => {
                                e.stopPropagation();
                                handleCheckboxChange(fullKey, e.target.checked);
                            }}
                            className="flex-shrink-0"
                        />
                        {isExpanded ? (
                            <ChevronDown size={16} />
                        ) : (
                            <ChevronRight size={16} />
                        )}
                        <Target size={16} className="text-green-600" />
                        <span className="font-medium text-green-700">
                            {kazanimKey}
                        </span>
                        <span className="text-sm text-gray-600">
                            - {kazanim.baslik}
                        </span>
                    </div>
                </div>

                {isExpanded &&
                    kazanim.aciklama &&
                    renderFeAciklama(kazanim.aciklama, kazanimKey)}
            </div>
        );
    };

    const renderFeKonu = (konu: FeKonu, konuKey: string, parentKey: string) => {
        const fullKey = `${parentKey}-${konuKey}`;
        const isExpanded = expandedItems.has(fullKey);

        return (
            <div key={konuKey} className="ml-2">
                <div
                    className="p-4 rounded-lg border cursor-pointer transition-colors bg-white border-gray-200 hover:bg-gray-50"
                >
                    <div className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            checked={checkedItems.has(fullKey)}
                            onChange={(e) => {
                                e.stopPropagation();
                                handleCheckboxChange(fullKey, e.target.checked);
                            }}
                            className="flex-shrink-0"
                        />
                        <div 
                            className="flex items-center gap-2 flex-1 cursor-pointer"
                            onClick={() => {
                                toggleExpanded(fullKey);
                            }}
                        >
                            {isExpanded ? (
                                <ChevronDown size={18} />
                            ) : (
                                <ChevronRight size={18} />
                            )}
                            <Book size={18} className="text-purple-600" />
                            <span className="font-semibold text-purple-700">
                                {konuKey}
                            </span>
                        </div>
                    </div>
                </div>

                {isExpanded && (
                    <div className="mt-2 space-y-2">
                        {Object.entries(konu).map(([kazanimKey, kazanim]) =>
                            renderFeKazanim(kazanim, kazanimKey, fullKey),
                        )}
                    </div>
                )}
            </div>
        );
    };

    // Kimya tipi için render fonksiyonları
    const renderKiItem = (
        item: any,
        itemKey: string,
        parentKey: string,
        level: number = 0,
    ): JSX.Element => {
        const fullKey = `${parentKey}-${itemKey}`;
        const isExpanded = expandedItems.has(fullKey);
        const hasChildren = item.alt && Object.keys(item.alt).length > 0;

        const getColorByLevel = (level: number) => {
            const colors = [
                {
                    bg: "bg-blue-100",
                    border: "border-blue-300",
                    text: "text-blue-700",
                    icon: "text-blue-600",
                },
                {
                    bg: "bg-purple-100",
                    border: "border-purple-300",
                    text: "text-purple-700",
                    icon: "text-purple-600",
                },
                {
                    bg: "bg-green-100",
                    border: "border-green-300",
                    text: "text-green-700",
                    icon: "text-green-600",
                },
                {
                    bg: "bg-orange-100",
                    border: "border-orange-300",
                    text: "text-orange-700",
                    icon: "text-orange-600",
                },
                {
                    bg: "bg-pink-100",
                    border: "border-pink-300",
                    text: "text-pink-700",
                    icon: "text-pink-600",
                },
            ];
            return colors[level % colors.length];
        };

        const colors = getColorByLevel(level);

        return (
            <div key={itemKey} style={{ marginLeft: `${level * 16}px` }}>
                <div
                    className="p-3 rounded-lg border cursor-pointer transition-colors bg-white border-gray-200 hover:bg-gray-50"
                >
                    <div className="flex items-start gap-2">
                        <input
                            type="checkbox"
                            checked={checkedItems.has(fullKey)}
                            onChange={(e) => {
                                e.stopPropagation();
                                handleCheckboxChange(fullKey, e.target.checked);
                            }}
                            className="mt-1 flex-shrink-0"
                        />
                        <div 
                            className="flex items-start gap-2 flex-1 cursor-pointer"
                            onClick={() => {
                                if (hasChildren) {
                                    toggleExpanded(fullKey);
                                }
                            }}
                        >
                            {hasChildren &&
                                (isExpanded ? (
                                    <ChevronDown size={16} />
                                ) : (
                                    <ChevronRight size={16} />
                                ))}
                            {!hasChildren && <div className="w-4" />}
                            <Hash size={16} className={colors.icon} />
                            <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                                <span className={`font-medium ${colors.text}`}>
                                    {itemKey}
                                </span>
                                <span className="text-sm text-gray-600">
                                    - {item.baslik}
                                </span>
                            </div>

                            {item.anahtar_kavramlar && (
                                <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded mt-1">
                                    <strong>Anahtar Kavramlar:</strong>{" "}
                                    {item.anahtar_kavramlar}
                                </div>
                            )}

                            {item.aciklama &&
                                Object.keys(item.aciklama).length > 0 && (
                                    <div className="mt-2 space-y-1">
                                        {Object.entries(item.aciklama).map(
                                            ([key, value]) => (
                                                <div
                                                    key={key}
                                                    className="text-xs text-gray-600 bg-gray-50 p-2 rounded"
                                                >
                                                    <strong>{key}:</strong>{" "}
                                                    {value as string}
                                                </div>
                                            ),
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {isExpanded && hasChildren && (
                    <div className="mt-2 space-y-2">
                        {Object.entries(item.alt).map(([subKey, subItem]) =>
                            renderKiItem(subItem, subKey, fullKey, level + 1),
                        )}
                    </div>
                )}
            </div>
        );
    };

    const renderKiSinif = (sinif: KiSinif, sinifKey: string) => {
        const fullSinifKey = `${selectedDers}-${sinifKey}`;
        const isExpanded = expandedItems.has(fullSinifKey);

        return (
            <div key={sinifKey} className="mb-4">
                <div
                    className="p-4 rounded-lg border cursor-pointer transition-colors bg-white border-gray-300 hover:bg-gray-50"
                >
                    <div className="flex items-center gap-3">
                        <input
                            type="checkbox"
                            checked={checkedItems.has(`${selectedDers}-${sinifKey}`)}
                            onChange={(e) => {
                                e.stopPropagation();
                                handleCheckboxChange(`${selectedDers}-${sinifKey}`, e.target.checked);
                            }}
                            className="flex-shrink-0"
                        />
                        <div 
                            className="flex items-center gap-3 flex-1 cursor-pointer"
                            onClick={() => {
                                toggleExpanded(fullSinifKey);
                                handleSelect({
                                    ders: selectedDers,
                                    sinif: sinifKey,
                                });
                            }}
                        >
                            {isExpanded ? (
                                <ChevronDown size={20} />
                            ) : (
                                <ChevronRight size={20} />
                            )}
                            <BookOpen size={20} className="text-blue-600" />
                            <span className="text-lg font-bold text-blue-700">
                                {sinifKey}. Sınıf
                            </span>
                        </div>
                    </div>
                </div>

                {isExpanded && sinif.alt && (
                    <div className="mt-3 space-y-3">
                        {Object.entries(sinif.alt).map(([konuKey, konu]) =>
                            renderKiItem(konu, konuKey, `${selectedDers}-${sinifKey}`, 0),
                        )}
                    </div>
                )}
            </div>
        );
    };

    // Felsefe tipi için sınıf render
    const renderFeSinif = (sinif: FeSinif, sinifKey: string) => {
        const fullSinifKey = `${selectedDers}-${sinifKey}`;
        const isExpanded = expandedItems.has(fullSinifKey);

        return (
            <div key={sinifKey} className="mb-4">
                <div
                    className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                        selectedItem?.sinif === sinifKey && !selectedItem?.konu
                            ? "bg-blue-100 border-blue-300"
                            : "bg-white border-gray-300 hover:bg-gray-50"
                    }`}
                >
                    <div className="flex items-center gap-3">
                        <input
                            type="checkbox"
                            checked={checkedItems.has(`${selectedDers}-${sinifKey}`)}
                            onChange={(e) => {
                                e.stopPropagation();
                                handleCheckboxChange(`${selectedDers}-${sinifKey}`, e.target.checked);
                            }}
                            className="flex-shrink-0"
                        />
                        <div 
                            className="flex items-center gap-3 flex-1 cursor-pointer"
                            onClick={() => {
                                toggleExpanded(fullSinifKey);
                                handleSelect({
                                    ders: selectedDers,
                                    sinif: sinifKey,
                                });
                            }}
                        >
                            {isExpanded ? (
                                <ChevronDown size={20} />
                            ) : (
                                <ChevronRight size={20} />
                            )}
                            <BookOpen size={20} className="text-blue-600" />
                            <span className="text-lg font-bold text-blue-700">
                                {sinifKey}. Sınıf
                            </span>
                        </div>
                    </div>
                </div>

                {isExpanded && (
                    <div className="mt-3 space-y-3">
                        {Object.entries(sinif).map(([konuKey, konu]) =>
                            renderFeKonu(konu, konuKey, `${selectedDers}-${sinifKey}`),
                        )}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="max-w-7xl mx-auto p-6 bg-gray-50 min-h-screen">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">
                    YKS Dersleri ve Kazanımları
                </h1>
                <p className="text-gray-600">
                    Ders seçerek kazanımları detaylı şekilde inceleyebilirsiniz.
                </p>
            </div>

            {/* Ders Seçim Butonları */}
            <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4 text-gray-700">
                    Ders Seçin:
                </h2>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                    {YKS_DERSLERI.map((ders) => (
                        <div
                            key={ders.name}
                            onClick={() => handleDersSelect(ders.name)}
                            className={`p-3 rounded-lg border transition-all cursor-pointer ${
                                selectedDers === ders.name
                                    ? "bg-blue-600 text-white border-blue-600 shadow-lg"
                                    : "bg-white text-gray-700 border-gray-200 hover:bg-blue-50 hover:border-blue-300"
                            }`}
                        >
                            <div className="text-sm font-medium">
                                {ders.displayName}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Seçim Paneli */}
            {selectedDers && (
                <div className="mb-8 bg-white rounded-lg border border-gray-200 p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-gray-800">
                            Seçilen Konular ({checkedItems.size})
                        </h2>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setShowSelectionPanel(!showSelectionPanel)}
                                className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                            >
                                {showSelectionPanel ? "Gizle" : "Göster"}
                            </button>
                            <button
                                onClick={clearAllSelections}
                                className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200"
                                disabled={checkedItems.size === 0}
                            >
                                Tümünü Temizle
                            </button>
                        </div>
                    </div>

                    {showSelectionPanel && checkedItems.size > 0 && (
                        <div className="space-y-2 max-h-60 overflow-y-auto">
                            {getSelectedItemsData().map((item) => (
                                <div key={item.id} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                                    <div>
                                        <span className="text-sm font-medium">{item.title}</span>
                                        <div className="text-xs text-gray-500">
                                            {item.type === "ders" && "Ders"}
                                            {item.type === "sinif" && "Sınıf"}
                                            {item.type === "konu" && "Konu"}
                                            {item.type === "kazanim" && "Kazanım"}
                                            {item.type === "aciklama" && "Açıklama"}
                                            {item.sinif && ` • ${item.sinif}. Sınıf`}
                                            {item.konu && ` • ${item.konu}`}
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => handleCheckboxChange(item.id, false)}
                                        className="text-red-500 hover:text-red-700 text-sm"
                                    >
                                        Kaldır
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    {checkedItems.size === 0 && (
                        <p className="text-gray-500 text-sm">
                            Henüz hiç konu seçilmedi. Aşağıdaki kazanımlardan seçim yapabilirsiniz.
                        </p>
                    )}

                    {/* Devam Et Butonu ve İşlevler */}
                    {checkedItems.size > 0 && (
                        <div className="mt-6 border-t pt-6">
                            <h3 className="text-lg font-semibold text-gray-800 mb-4">
                                Seçilen Konularla Devam Et
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                <button
                                    onClick={() => handleCurriculumAction('questions')}
                                    className="flex items-center gap-2 px-4 py-3 bg-green-100 text-green-800 rounded-lg hover:bg-green-200 transition-colors"
                                >
                                    <span className="text-lg">❓</span>
                                    <div className="text-left">
                                        <div className="font-medium">Soru Hazırla</div>
                                        <div className="text-xs">Seçilen konulardan sorular oluştur</div>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleCurriculumAction('summary')}
                                    className="flex items-center gap-2 px-4 py-3 bg-blue-100 text-blue-800 rounded-lg hover:bg-blue-200 transition-colors"
                                >
                                    <span className="text-lg">📝</span>
                                    <div className="text-left">
                                        <div className="font-medium">Konu Özetle</div>
                                        <div className="text-xs">Kapsamlı özet hazırla</div>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleCurriculumAction('concept-map')}
                                    className="flex items-center gap-2 px-4 py-3 bg-purple-100 text-purple-800 rounded-lg hover:bg-purple-200 transition-colors"
                                >
                                    <span className="text-lg">🗺️</span>
                                    <div className="text-left">
                                        <div className="font-medium">Kavram Haritası</div>
                                        <div className="text-xs">Mantık bağlantıları oluştur</div>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleCurriculumAction('explanation')}
                                    className="flex items-center gap-2 px-4 py-3 bg-orange-100 text-orange-800 rounded-lg hover:bg-orange-200 transition-colors"
                                >
                                    <span className="text-lg">📚</span>
                                    <div className="text-left">
                                        <div className="font-medium">Konu Anlatımı</div>
                                        <div className="text-xs">Detaylı açıklama</div>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleCurriculumAction('ai-chat')}
                                    className="flex items-center gap-2 px-4 py-3 bg-cyan-100 text-cyan-800 rounded-lg hover:bg-cyan-200 transition-colors"
                                >
                                    <span className="text-lg">🤖</span>
                                    <div className="text-left">
                                        <div className="font-medium">AI ile Devam Et</div>
                                        <div className="text-xs">Serbest sohbet ve sorular</div>
                                    </div>
                                </button>

                                <button
                                    onClick={() => handleCurriculumAction('socratic')}
                                    className="flex items-center gap-2 px-4 py-3 bg-yellow-100 text-yellow-800 rounded-lg hover:bg-yellow-200 transition-colors"
                                >
                                    <span className="text-lg">🎯</span>
                                    <div className="text-left">
                                        <div className="font-medium">Sokratik AI</div>
                                        <div className="text-xs">Soru-cevap öğrenme</div>
                                    </div>
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Yükleme Durumu */}
            {loading && (
                <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">
                        Kazanımlar yükleniyor...
                    </p>
                </div>
            )}

            {/* Hata Durumu */}
            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
                    {error}
                </div>
            )}


            {/* Kazanımlar */}
            {dersData && selectedDers && dersData.yks[selectedDers] && (
                <div className="space-y-4">
                    <h2 className="text-2xl font-bold text-gray-800 mb-6">
                        {
                            YKS_DERSLERI.find((d) => d.name === selectedDers)
                                ?.displayName
                        }{" "}
                        Kazanımları
                    </h2>

                    {isDersKimyaType(dersData, selectedDers)
                        ? // Kimya tipi yapı
                          Object.entries(
                              dersData.yks[selectedDers] as KiDers,
                          ).map(([sinifKey, sinif]) =>
                              renderKiSinif(sinif, sinifKey),
                          )
                        : // Felsefe tipi yapı
                          Object.entries(
                              dersData.yks[selectedDers] as FeDers,
                          ).map(([sinifKey, sinif]) =>
                              renderFeSinif(sinif, sinifKey),
                          )}
                </div>
            )}

            {/* Ders seçilmediğinde */}
            {!selectedDers && (
                <div className="text-center py-12">
                    <BookOpen
                        size={48}
                        className="mx-auto text-gray-400 mb-4"
                    />
                    <h3 className="text-xl font-semibold text-gray-600 mb-2">
                        Ders Seçin
                    </h3>
                    <p className="text-gray-500">
                        Kazanımları görüntülemek için yukarıdan bir ders seçin.
                    </p>
                </div>
            )}
        </div>
    );
};

export default YKSKazanimlar;

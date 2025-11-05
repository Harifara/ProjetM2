import React, { useEffect, useState } from "react";
import { rhApi } from "@/lib/api";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Toaster } from "@/components/ui/toaster";

import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import * as XLSX from "xlsx";

import logo from "@/assets/logo.jpg";

interface District {
  id?: string;
  name: string;
  code: string;
  region: string;
}

const Districts = () => {
  const [districts, setDistricts] = useState<District[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDistrict, setEditingDistrict] = useState<District | null>(null);
  const [form, setForm] = useState<District>({
    name: "",
    code: "",
    region: "",
  });

  const fetchDistricts = async () => {
    setLoading(true);
    try {
      const data = await rhApi.getDistricts();
      setDistricts(data);
    } catch (err: any) {
      alert(err.message || "Erreur lors du chargement des districts");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchDistricts();
  }, []);

  const openAddModal = () => {
    setEditingDistrict(null);
    setForm({ name: "", code: "", region: "" });
    setIsModalOpen(true);
  };

  const openEditModal = (district: District) => {
    setEditingDistrict(district);
    setForm(district);
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingDistrict) {
        await rhApi.updateDistrict(editingDistrict.id!, form);
      } else {
        await rhApi.createDistrict(form);
      }
      fetchDistricts();
      setIsModalOpen(false);
    } catch (err: any) {
      alert(err.message || "Erreur lors de l'enregistrement");
    }
  };

  // 🧾 Export PDF corrigé
  const exportPDF = async () => {
    const doc = new jsPDF("p", "pt");
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();

    // Charger le logo de manière synchrone avec base64
    const toBase64 = (url: string) =>
      new Promise<string>((resolve, reject) => {
        const img = new Image();
        img.crossOrigin = "Anonymous";
        img.onload = function () {
          const canvas = document.createElement("canvas");
          canvas.width = img.width;
          canvas.height = img.height;
          const ctx = canvas.getContext("2d");
          if (!ctx) return reject("Impossible de charger le logo");
          ctx.drawImage(img, 0, 0);
          resolve(canvas.toDataURL("image/jpeg"));
        };
        img.onerror = reject;
        img.src = url;
      });

    const logoBase64 = await toBase64(logo);

    // === En-tête (uniquement sur la 1ʳᵉ page) ===
    const addHeader = () => {
      const logoWidth = 90;
      const logoHeight = 90;
      const logoX = pageWidth - logoWidth - 50;
      const logoY = 45;
      doc.addImage(logoBase64, "JPEG", logoX, logoY, logoWidth, logoHeight);

      const startX = 60;
      let y = 55;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(8);
      doc.text(
        "Espace Chrétien des Actions en Redressement de Tsihombe",
        startX,
        y
      );

      y += 12;
      doc.setFont("helvetica", "bold");
      doc.text('ASSOCIATION "E.C.A.R.T"', startX + 85, y);

      y += 12;
      doc.setFont("helvetica", "normal");
      doc.text("Récépissé : N° 39-2012/REG/ANDROY/CR/SG/DAGT/ASS", startX, y);

      y += 12;
      doc.text("NIF N°: 6002559762", startX + 60, y);

      y += 12;
      doc.text("STAT : 88101620213000298", startX + 40, y);

      y += 12;
      doc.text("Téléphone(s): 033 91 635 59 / 034 80 893 01", startX, y);

      y += 12;
      doc.text("E-mail: ecarmada4@gmail.com", startX + 60, y);

      // Ligne séparatrice
      y += 15;
      doc.setDrawColor(0);
      doc.setLineWidth(0.3);
      doc.line(40, y, pageWidth - 40, y);

      // Titre principal
      y += 25;
      doc.setFontSize(12);
      doc.setFont("helvetica", "bold");
      doc.text("LISTE DES DISTRICTS", pageWidth / 2, y, { align: "center" });

      return y + 20;
    };

    const startY = addHeader();

    // === Tableau ===
    autoTable(doc, {
      startY,
      head: [["Nom", "Code", "Région"]],
      body: districts.map((d) => [d.name, d.code, d.region]),
      styles: {
        fontSize: 8,
        cellPadding: 5,
        halign: "center",
        valign: "middle",
      },
      headStyles: {
        fillColor: [41, 128, 185],
        textColor: 255,
        halign: "center",
        valign: "middle",
      },
      alternateRowStyles: { fillColor: [245, 245, 245] },
      margin: { left: 40, right: 40 },
      didDrawPage: (data) => {
        const pageCount = doc.internal.getNumberOfPages();
        const currentPage = doc.internal.getCurrentPageInfo().pageNumber;

        doc.setFontSize(8);
        doc.setFont("helvetica", "italic");
        doc.text(
          `Page ${currentPage} / ${pageCount}`,
          pageWidth - 80,
          pageHeight - 20
        );
      },
    });

    doc.save("districts.pdf");
  };

  const exportExcel = () => {
    const worksheet = XLSX.utils.json_to_sheet(
      districts.map((d) => ({
        Nom: d.name,
        Code: d.code,
        Région: d.region,
      }))
    );
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Districts");
    XLSX.writeFile(workbook, "districts.xlsx");
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Liste des Districts</h2>

      <div className="mb-4 flex gap-2">
        <Button onClick={openAddModal}>Ajouter un District</Button>
        <Button onClick={exportPDF} variant="outline">
          Exporter PDF
        </Button>
        <Button onClick={exportExcel} variant="outline">
          Exporter Excel
        </Button>
      </div>

      {loading ? (
        <p>Chargement...</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nom</TableHead>
              <TableHead>Code</TableHead>
              <TableHead>Région</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {districts.map((d) => (
              <TableRow key={d.id}>
                <TableCell>{d.name}</TableCell>
                <TableCell>{d.code}</TableCell>
                <TableCell>{d.region}</TableCell>
                <TableCell>
                  <Button size="sm" onClick={() => openEditModal(d)}>
                    Modifier
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingDistrict ? "Modifier District" : "Ajouter District"}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <Input
              placeholder="Nom"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
            <Input
              placeholder="Code"
              value={form.code}
              onChange={(e) => setForm({ ...form, code: e.target.value })}
            />
            <Input
              placeholder="Région"
              value={form.region}
              onChange={(e) => setForm({ ...form, region: e.target.value })}
            />
          </div>
          <DialogFooter>
            <Button onClick={handleSubmit}>
              {editingDistrict ? "Modifier" : "Ajouter"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Toaster />
    </div>
  );
};

export default Districts;

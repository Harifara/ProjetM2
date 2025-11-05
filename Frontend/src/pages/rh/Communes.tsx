import React, { useEffect, useState } from "react";
import { rhApi } from "@/lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";

interface Commune {
  id?: string;
  name: string;
  code: string;
  district: { id: string; name: string };
}

interface District {
  id: string;
  name: string;
}

const Communes = () => {
  const [communes, setCommunes] = useState<Commune[]>([]);
  const [districts, setDistricts] = useState<District[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editing, setEditing] = useState<Commune | null>(null);
  const [form, setForm] = useState<Commune>({
    name: "",
    code: "",
    district: { id: "", name: "" },
  });

  const fetchCommunes = async () => {
    setLoading(true);
    try {
      const data = await rhApi.getCommunes();
      setCommunes(data);
      const dist = await rhApi.getDistricts();
      setDistricts(dist);
    } catch (err: any) {
      alert(err.message);
    }
    setLoading(false);
  };

  useEffect(() => { fetchCommunes(); }, []);

  const openAddModal = () => {
    setEditing(null);
    setForm({ name: "", code: "", district: { id: "", name: "" }});
    setIsModalOpen(true);
  };

  const openEditModal = (c: Commune) => {
    setEditing(c);
    setForm(c);
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      // Préparer le payload pour l'API
      const payload = {
        ...form,
        district_id: form.district.id, // envoyer district_id au lieu de l'objet district
      };
      delete (payload as any).district;

      if (editing) await rhApi.updateCommune(editing.id!, payload);
      else await rhApi.createCommune(payload);

      fetchCommunes();
      setIsModalOpen(false);
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Communes</h2>
      <Button onClick={openAddModal} className="mb-2">Ajouter une Commune</Button>
      {loading ? <p>Chargement...</p> : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nom</TableHead>
              <TableHead>Code</TableHead>
              <TableHead>District</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {communes.map(c => (
              <TableRow key={c.id}>
                <TableCell>{c.name}</TableCell>
                <TableCell>{c.code}</TableCell>
                <TableCell>{c.district.name}</TableCell>
                <TableCell><Button size="sm" onClick={() => openEditModal(c)}>Modifier</Button></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? "Modifier" : "Ajouter"} Commune</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <Input
              placeholder="Nom"
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
            />
            <Input
              placeholder="Code"
              value={form.code}
              onChange={e => setForm({ ...form, code: e.target.value })}
            />
            <Select
              value={form.district.id}
              onValueChange={val => {
                const selected = districts.find(d => d.id === val);
                if (selected) setForm({ ...form, district: selected });
              }}
            >
              <SelectTrigger>
                <SelectValue placeholder="Choisir un District" />
              </SelectTrigger>
              <SelectContent>
                {districts.map(d => (
                  <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button onClick={handleSubmit}>{editing ? "Modifier" : "Ajouter"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Communes;

// src/pages/rh/Fokontanys.tsx
import React, { useEffect, useState } from "react";
import { rhApi } from "@/lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";

interface Fokontany {
  id?: string;
  name: string;
  code: string;
  commune: { id: string; name: string; district: { id: string; name: string } };
}

interface Commune {
  id: string;
  name: string;
  district: { id: string; name: string };
}

const Fokontanys = () => {
  const [fokontanys, setFokontanys] = useState<Fokontany[]>([]);
  const [communes, setCommunes] = useState<Commune[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editing, setEditing] = useState<Fokontany | null>(null);
  const [form, setForm] = useState<Fokontany>({
    name: "",
    code: "",
    commune: { id: "", name: "", district: { id: "", name: "" } },
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const fok = await rhApi.getFokontanys();
      const com = await rhApi.getCommunes();
      setFokontanys(fok);
      setCommunes(com);
    } catch (err: any) {
      alert(err.message);
    }
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, []);

  const openAddModal = () => {
    setEditing(null);
    setForm({ name: "", code: "", commune: { id: "", name: "", district: { id: "", name: "" } }});
    setIsModalOpen(true);
  };

  const openEditModal = (f: Fokontany) => {
    setEditing(f);
    setForm(f);
    setIsModalOpen(true);
  };

  const handleSubmit = async () => {
    try {
      // Préparer le payload attendu par l'API
      const payload = {
        ...form,
        commune_id: form.commune.id, // envoyer commune_id
      };
      delete (payload as any).commune;

      if (editing) await rhApi.updateFokontany(editing.id!, payload);
      else await rhApi.createFokontany(payload);

      fetchData();
      setIsModalOpen(false);
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Fokontanies</h2>
      <Button onClick={openAddModal} className="mb-2">Ajouter un Fokontany</Button>
      {loading ? <p>Chargement...</p> : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nom</TableHead>
              <TableHead>Code</TableHead>
              <TableHead>Commune</TableHead>
              <TableHead>District</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {fokontanys.map(f => (
              <TableRow key={f.id}>
                <TableCell>{f.name}</TableCell>
                <TableCell>{f.code}</TableCell>
                <TableCell>{f.commune.name}</TableCell>
                <TableCell>{f.commune.district.name}</TableCell>
                <TableCell>
                  <Button size="sm" onClick={() => openEditModal(f)}>Modifier</Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? "Modifier" : "Ajouter"} Fokontany</DialogTitle>
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
              value={form.commune.id}
              onValueChange={val => {
                const selected = communes.find(c => c.id === val);
                if (selected) setForm({ ...form, commune: selected });
              }}
            >
              <SelectTrigger><SelectValue placeholder="Choisir une Commune" /></SelectTrigger>
              <SelectContent>
                {communes.map(c => <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>)}
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

export default Fokontanys;

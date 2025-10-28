import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { rhApi } from "@/lib/api";
import CommuneModal from "@/components/rh/CommuneModal";

interface Commune {
  id: string;
  name: string;
}

const RHCommunes = () => {
  const [communes, setCommunes] = useState<Commune[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedCommune, setSelectedCommune] = useState<Commune | null>(null);

  const fetchCommunes = async () => {
    setLoading(true);
    try {
      const data = await rhApi.getCommunes();
      setCommunes(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCommunes();
  }, []);

  const handleEdit = (commune: Commune) => {
    setSelectedCommune(commune);
    setModalOpen(true);
  };

  return (
    <div>
      <Card>
        <CardHeader className="flex justify-between items-center">
          <CardTitle>Communes</CardTitle>
          <Button onClick={() => setModalOpen(true)}>Ajouter une commune</Button>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>Chargement...</p>
          ) : (
            <table className="w-full table-auto border-collapse">
              <thead>
                <tr>
                  <th className="border p-2 text-left">ID</th>
                  <th className="border p-2 text-left">Nom</th>
                  <th className="border p-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {communes.map((c) => (
                  <tr key={c.id}>
                    <td className="border p-2">{c.id}</td>
                    <td className="border p-2">{c.name}</td>
                    <td className="border p-2">
                      <Button size="sm" onClick={() => handleEdit(c)}>Modifier</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      {modalOpen && (
        <CommuneModal
          commune={selectedCommune}
          onClose={() => { setModalOpen(false); setSelectedCommune(null); fetchCommunes(); }}
        />
      )}
    </div>
  );
};

export default RHCommunes;

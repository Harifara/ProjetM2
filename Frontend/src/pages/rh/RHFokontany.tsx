import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { rhApi } from "@/lib/api";
import FokontanyModal from "@/components/rh/FokontanyModal";

interface Fokontany {
  id: string;
  name: string;
}

const RHFokontany = () => {
  const [fokontany, setFokontany] = useState<Fokontany[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedFokontany, setSelectedFokontany] = useState<Fokontany | null>(null);

  const fetchFokontany = async () => {
    setLoading(true);
    try {
      const data = await rhApi.getFokontany();
      setFokontany(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFokontany();
  }, []);

  const handleEdit = (f: Fokontany) => {
    setSelectedFokontany(f);
    setModalOpen(true);
  };

  return (
    <div>
      <Card>
        <CardHeader className="flex justify-between items-center">
          <CardTitle>Fokontany</CardTitle>
          <Button onClick={() => setModalOpen(true)}>Ajouter un fokontany</Button>
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
                {fokontany.map((f) => (
                  <tr key={f.id}>
                    <td className="border p-2">{f.id}</td>
                    <td className="border p-2">{f.name}</td>
                    <td className="border p-2">
                      <Button size="sm" onClick={() => handleEdit(f)}>Modifier</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      {modalOpen && (
        <FokontanyModal
          fokontany={selectedFokontany}
          onClose={() => { setModalOpen(false); setSelectedFokontany(null); fetchFokontany(); }}
        />
      )}
    </div>
  );
};

export default RHFokontany;

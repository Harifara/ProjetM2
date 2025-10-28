import React, { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { rhApi } from "@/lib/api";
import DistrictModal from "@/components/rh/DistrictModal";

interface District {
  id: string; // UUID
  name: string;
}

const RHDistricts = () => {
  const [districts, setDistricts] = useState<District[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedDistrict, setSelectedDistrict] = useState<District | null>(null);

  // ✅ Fetch districts
  const fetchDistricts = async () => {
    setLoading(true);
    setError(null);
    try {
      const data: District[] = await rhApi.getDistricts();
      setDistricts(data);
    } catch (err) {
      console.error("Erreur lors de la récupération des districts :", err);
      setError("Impossible de récupérer les districts.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDistricts();
  }, []);

  // ✅ Ouvrir modal pour ajout/modification
  const handleEdit = (district: District) => {
    setSelectedDistrict(district);
    setModalOpen(true);
  };

  // ✅ Supprimer un district
  const handleDelete = async (id: string) => {
    if (!confirm("Voulez-vous vraiment supprimer ce district ?")) return;
    try {
      await rhApi.deleteDistrict(id);
      setDistricts(prev => prev.filter(d => d.id !== id));
    } catch (err) {
      console.error("Erreur lors de la suppression du district :", err);
      setError("Impossible de supprimer ce district.");
    }
  };

  // ✅ Mettre à jour la liste après ajout/modification
  const handleModalClose = (updatedDistrict?: District) => {
    setModalOpen(false);
    setSelectedDistrict(null);
    if (updatedDistrict) {
      // Si c'est une modification, on met à jour le tableau
      setDistricts(prev => {
        const exists = prev.find(d => d.id === updatedDistrict.id);
        if (exists) {
          return prev.map(d => d.id === updatedDistrict.id ? updatedDistrict : d);
        }
        // Sinon, c'est un ajout, on ajoute en haut
        return [updatedDistrict, ...prev];
      });
    } else {
      // Si fermeture sans modification, on peut refetch
      fetchDistricts();
    }
  };

  return (
    <div>
      <Card>
        <CardHeader className="flex justify-between items-center">
          <CardTitle>Districts</CardTitle>
          <Button onClick={() => { setSelectedDistrict(null); setModalOpen(true); }}>
            Ajouter un district
          </Button>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p>Chargement...</p>
          ) : error ? (
            <p className="text-red-600">{error}</p>
          ) : (
            <table className="w-full table-auto border-collapse">
              <thead>
                <tr>
                  <th className="border p-2 text-left">ID</th>
                  <th className="border p-2 text-left">Nom</th>
                  <th className="border p-2 text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {districts.map(d => (
                  <tr key={d.id}>
                    <td className="border p-2">{d.id}</td>
                    <td className="border p-2">{d.name}</td>
                    <td className="border p-2 flex justify-center gap-2">
                      <Button size="sm" onClick={() => handleEdit(d)}>Modifier</Button>
                      <Button size="sm" variant="destructive" onClick={() => handleDelete(d.id)}>Supprimer</Button>
                    </td>
                  </tr>
                ))}
                {districts.length === 0 && (
                  <tr>
                    <td colSpan={3} className="border p-2 text-center">Aucun district trouvé.</td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      {modalOpen && (
        <DistrictModal
          district={selectedDistrict}
          onClose={handleModalClose}
        />
      )}
    </div>
  );
};

export default RHDistricts;

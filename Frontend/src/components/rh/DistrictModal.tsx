import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { rhApi } from "@/lib/api";

interface District {
  id?: string; // UUID
  name: string;
}

interface Props {
  district: District | null;
  onClose: () => void;
}

const DistrictModal: React.FC<Props> = ({ district, onClose }) => {
  const [name, setName] = useState("");

  useEffect(() => {
    if (district) setName(district.name);
    else setName("");
  }, [district]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (district?.id) {
        // update
        await rhApi.updateDistrict(district.id, { name });
      } else {
        // create
        await rhApi.createDistrict({ name });
      }
      onClose();
    } catch (err) {
      console.error("Erreur lors de l'enregistrement :", err);
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white p-6 rounded shadow-lg w-96">
        <h2 className="text-lg font-bold mb-4">{district ? "Modifier" : "Ajouter"} un district</h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Nom du district"
            className="border p-2 rounded"
            required
          />
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>Annuler</Button>
            <Button type="submit">{district ? "Modifier" : "Ajouter"}</Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DistrictModal;

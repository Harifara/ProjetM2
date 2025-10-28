import React, { useState } from "react";
import { rhApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";

interface Props {
  commune: { id?: number; name: string } | null;
  onClose: () => void;
}

const CommuneModal: React.FC<Props> = ({ commune, onClose }) => {
  const [name, setName] = useState(commune?.name || "");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      if (commune?.id) {
        await rhApi.updateCommune(commune.id, { name });
      } else {
        await rhApi.createCommune({ name });
      }
      onClose();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{commune ? "Modifier Commune" : "Ajouter Commune"}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 mt-2">
          <input
            type="text"
            className="w-full border p-2 rounded"
            placeholder="Nom de la commune"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <DialogFooter>
          <Button onClick={onClose} variant="outline">Annuler</Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? "En cours..." : "Enregistrer"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CommuneModal;

import React, { useState } from "react";
import { rhApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";

interface Props {
  fokontany: { id?: number; name: string } | null;
  onClose: () => void;
}

const FokontanyModal: React.FC<Props> = ({ fokontany, onClose }) => {
  const [name, setName] = useState(fokontany?.name || "");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      if (fokontany?.id) {
        await rhApi.updateFokontany(fokontany.id, { name });
      } else {
        await rhApi.createFokontany({ name });
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
          <DialogTitle>{fokontany ? "Modifier Fokontany" : "Ajouter Fokontany"}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 mt-2">
          <input
            type="text"
            className="w-full border p-2 rounded"
            placeholder="Nom du fokontany"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>
        <DialogFooter className="space-x-2">
          <Button onClick={onClose} variant="outline">Annuler</Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? "En cours..." : "Enregistrer"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default FokontanyModal;

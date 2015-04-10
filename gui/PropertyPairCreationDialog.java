/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package gui;

import propsandcovariants.Covariant;
import propsandcovariants.EligibleCovariantTableModel;
import propsandcovariants.CovariantPairing;
import propsandcovariants.CovariantPairingsManager;
import misc.ExactlyOneRowSelectionModel;

/**
 *
 * @author Henry
 */
public class PropertyPairCreationDialog extends javax.swing.JDialog {

   /** 
    * Creates new form PropertyPairCreationDialog
    */
   public PropertyPairCreationDialog(java.awt.Frame parent, boolean modal) {
      super(parent, modal);  
      initComponents();
      independentVarTable_.setSelectionModel(new ExactlyOneRowSelectionModel());
      dependentVarTable_.setSelectionModel(new ExactlyOneRowSelectionModel());
      setVisible(true);    
   }

   /**
    * This method is called from within the constructor to initialize the form.
    * WARNING: Do NOT modify this code. The content of this method is always
    * regenerated by the Form Editor.
    */
   @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        jScrollPane1 = new javax.swing.JScrollPane();
        independentVarTable_ = new javax.swing.JTable();
        jScrollPane2 = new javax.swing.JScrollPane();
        dependentVarTable_ = new javax.swing.JTable();
        cancelButton_ = new javax.swing.JButton();
        okButton_ = new javax.swing.JButton();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Select one from each list to create pairing");

        independentVarTable_.setModel(new EligibleCovariantTableModel(true));
        jScrollPane1.setViewportView(independentVarTable_);

        dependentVarTable_.setModel(new EligibleCovariantTableModel(false));
        jScrollPane2.setViewportView(dependentVarTable_);

        cancelButton_.setText("Cancel");
        cancelButton_.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                cancelButton_ActionPerformed(evt);
            }
        });

        okButton_.setText("OK");
        okButton_.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                okButton_ActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(jScrollPane1, javax.swing.GroupLayout.PREFERRED_SIZE, 408, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(okButton_, javax.swing.GroupLayout.PREFERRED_SIZE, 66, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(cancelButton_)
                        .addContainerGap(361, Short.MAX_VALUE))
                    .addComponent(jScrollPane2, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)))
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane1)
                    .addComponent(jScrollPane2))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(okButton_)
                    .addComponent(cancelButton_))
                .addContainerGap())
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

   private void cancelButton_ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_cancelButton_ActionPerformed
      this.dispose();
   }//GEN-LAST:event_cancelButton_ActionPerformed

   private void okButton_ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_okButton_ActionPerformed
      CovariantPairingsManager.getInstance().addPair(new CovariantPairing(
              (Covariant)((EligibleCovariantTableModel)independentVarTable_.getModel()).getValueAt(independentVarTable_.getSelectedRow(), 0),
              (Covariant)((EligibleCovariantTableModel)dependentVarTable_.getModel()).getValueAt(dependentVarTable_.getSelectedRow(), 0) ));
      dispose();
   }//GEN-LAST:event_okButton_ActionPerformed

   /**
    * @param args the command line arguments
    */
   public static void main(String args[]) {
      /*
       * Set the Nimbus look and feel
       */
      //<editor-fold defaultstate="collapsed" desc=" Look and feel setting code (optional) ">
        /*
       * If Nimbus (introduced in Java SE 6) is not available, stay with the
       * default look and feel. For details see
       * http://download.oracle.com/javase/tutorial/uiswing/lookandfeel/plaf.html
       */
      try {
         for (javax.swing.UIManager.LookAndFeelInfo info : javax.swing.UIManager.getInstalledLookAndFeels()) {
            if ("Nimbus".equals(info.getName())) {
               javax.swing.UIManager.setLookAndFeel(info.getClassName());
               break;
            }
         }
      } catch (ClassNotFoundException ex) {
         java.util.logging.Logger.getLogger(PropertyPairCreationDialog.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
      } catch (InstantiationException ex) {
         java.util.logging.Logger.getLogger(PropertyPairCreationDialog.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
      } catch (IllegalAccessException ex) {
         java.util.logging.Logger.getLogger(PropertyPairCreationDialog.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
      } catch (javax.swing.UnsupportedLookAndFeelException ex) {
         java.util.logging.Logger.getLogger(PropertyPairCreationDialog.class.getName()).log(java.util.logging.Level.SEVERE, null, ex);
      }
      //</editor-fold>

      /*
       * Create and display the dialog
       */
      java.awt.EventQueue.invokeLater(new Runnable() {

         public void run() {
            PropertyPairCreationDialog dialog = new PropertyPairCreationDialog(new javax.swing.JFrame(), true);
            dialog.addWindowListener(new java.awt.event.WindowAdapter() {

               @Override
               public void windowClosing(java.awt.event.WindowEvent e) {
                  System.exit(0);
               }
            });
            dialog.setVisible(true);
         }
      });
   }
    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton cancelButton_;
    private javax.swing.JTable dependentVarTable_;
    private javax.swing.JTable independentVarTable_;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JButton okButton_;
    // End of variables declaration//GEN-END:variables
}

package
{
   import flash.display.Loader;
   import flash.display.Sprite;
   import flash.net.URLRequest;
   import flash.system.ApplicationDomain;
   import flash.system.LoaderContext;

   import de.tosox.personal_spotted_alert.SpottedBulb;

   // Root of the markers movie in place of battleVehicleMarkersApp.swf, which
   // it loads as its only child. Both share one ApplicationDomain, so the
   // vanilla VehicleMarker.insertSymbol can create SpottedBulb by name
   public class PersonalSpottedAlertRoot extends Sprite
   {
      private static const APP_SWF:String = "battleVehicleMarkersApp.swf";

      // mxmlc only compiles classes that are referenced from the main class
      private static const CLASSES:Array = [SpottedBulb];

      // Lets Python tell that the markers movie runs through this root
      public const isPersonalSpottedAlertRoot:Boolean = true;

      private var _loader:Loader = null;

      public function PersonalSpottedAlertRoot()
      {
         super();
         this._loader = new Loader();
         addChild(this._loader);
         this._loader.load(new URLRequest(APP_SWF), new LoaderContext(false, ApplicationDomain.currentDomain));
      }

      // Python resolves 'root.vehicleMarkersCanvas' once the vanilla app has
      // loaded its libraries and called back, so its content is there by then
      public function get vehicleMarkersCanvas() : Object
      {
         var app:Object = this._loader.content;
         return app != null ? app.vehicleMarkersCanvas : null;
      }
   }
}
